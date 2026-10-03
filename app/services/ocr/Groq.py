import base64
import json
import os
import re
import urllib.error
import urllib.request

from app.services.ocr.imgconv import _render_pdf_pages_to_images

GROQ_MODEL = "qwen/qwen3.8-27b"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
REQUEST_TIMEOUT_SECONDS = 45


_PROMPT = """\
You are extracting a list of study topics from a college syllabus, \
shown to you as page images. Read the text in the images yourself \
(some pages may be low-quality scans) and infer the syllabus's real \
topic structure despite that.

Respond with a JSON object (and only JSON, no other text) shaped like:
{"units": [{"unit_name": "Unit or chapter title, or null if none", \
"topics": ["One specific, student-facing topic name", "..."]}]}

Each unit's topics are listed together under it ONCE — do not repeat \
the unit_name string for every topic; group all of a unit's topics \
into its single "topics" array instead. This keeps the response \
compact, which matters on this account's output-token limit.

Rules:
- Each topic string should be a single concrete thing a student would \
study and later be quizzed on — not a whole unit, not a vague heading \
like "Introduction", not exam-instruction boilerplate (e.g. "This \
paper carries 75 marks", page numbers, course codes).
- Split a topic that bundles several distinct concepts with commas or \
"and" into separate entries only if they are genuinely separate \
study topics, not if it's one continuous phrase.
- If this doesn't look like a syllabus at all, return {"units": []}.
"""

def _call_groq_with_images(page_images: list[bytes], api_key: str) -> tuple[str | None, str | None, float | None]:
 #                                                                    tuple[str or empty, float or empty]
    content = [{"type": "text", "text": _PROMPT}]


    for image_bytes in page_images:
        b64_data = base64.b64encode(image_bytes).decode("ascii") #encodes png into text

        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64_data}"},
        })
#       updated content = [{"type" = "text", "text" = _prompt}, {"url" = f string}]

    payload = json.dumps({ ##Creating JSON object - language for web communication
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": content}],
        "response_format": {"type": "json_object"}, #Response must be a JSON Object
        "reasoning_effort": "none",
        "max_tokens": 950,
    }).encode("utf-8") 


    request = urllib.request.Request(
        GROQ_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:


        try:
            detail = e.read().decode("utf-8")[:300]
        except Exception:
            detail = str(e)
        if "error code: 1010" in detail or "Cloudflare" in detail:
            return None, (
                "Blocked by Cloudflare (error 1010: browser signature "
                "banned) in front of Groq's API — this is a WAF-level "
                "block, not a Groq account/key problem. If this "
                "persists after the fix already in this file, Groq's "
                "edge network may be flagging something else about "
                "this request."
            ), None
        if e.code == 429:


            retry_after = e.headers.get("retry-after") if e.headers else None
            wait_seconds = None
            if retry_after:
                try:
                    wait_seconds = float(retry_after)
                except ValueError:
                    wait_seconds = None
            if wait_seconds is None:
                match = re.search(r"try again in ([\d.]+)s", detail)
                if match:
                    wait_seconds = float(match.group(1))
            if wait_seconds is not None:
                return None, (
                    f"Groq's free-tier rate limit was hit — try again "
                    f"in about {wait_seconds:.0f} seconds."
                ), wait_seconds
            return None, (
                "Groq's free-tier rate limit was hit — wait a minute "
                "and try again."
            ), None
        return None, f"Groq API returned HTTP {e.code}: {detail}", None
    except urllib.error.URLError as e:
        return None, f"Network error reaching Groq API: {e.reason}", None
    except TimeoutError:
        return None, f"Groq API call timed out after {REQUEST_TIMEOUT_SECONDS}s", None
    except json.JSONDecodeError:
        return None, "Groq API response was not valid JSON", None

    try:
        choice = body["choices"][0]
        content_text = choice["message"]["content"]
    except (KeyError, IndexError, TypeError):


        return None, f"Unexpected Groq response shape: {json.dumps(body)[:300]}", None

    if choice.get("finish_reason") == "length":


        return None, (
            "Groq's response was cut off (hit the max_tokens limit) — "
            "this syllabus has too many topics for one request under "
            "this account's rate limit. Try splitting it into smaller "
            "PDFs (e.g. one per unit), or increase max_tokens in "
            "pipeline.py if your account's rate limit allows it."
        ), None

    return content_text, None, None
