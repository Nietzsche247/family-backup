import json, os, uuid, urllib.request, urllib.error

BASE = "https://api.handwrytten.com/v2"
HERE = os.path.dirname(os.path.abspath(__file__))
KEY_DIRS = [HERE, r"C:\Users\aaron\clawd-shared"]

# ---- values below are NOT secret; the key is read from hw_key.txt ----
SENDER = {"first": "Omni Pool", "last": "Builders",
          "a1": "6640 N Oracle Rd Suite 130", "a2": "",
          "city": "Tucson", "state": "AZ", "zip": "85704"}
RECIP = {"first": "Michael & Jennifer", "last": "Baker",
         "a1": "12908 N Red Quail Pl", "a2": "",
         "city": "Marana", "state": "AZ", "zip": "85658"}
FONT = "Fancy Jenna"
IMG_URLS = ["https://picsum.photos/1500/1071.jpg",
            "https://dummyimage.com/1500x1071/336699/ffffff.jpg"]
# ----------------------------------------------------------------------


def find_key():
    for d in KEY_DIRS:
        for name in ("hw_key.txt", "hw_key.txt.txt", "hw_key"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    k = open(p, encoding="utf-8-sig").read().strip()
                except Exception:
                    continue
                if k:
                    return k
    return None


def req(path, method="GET", headers=None, data=None):
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")
    except Exception as e:
        return None, "ERROR: " + str(e)


def multipart(path, key, fields, filename, filebytes):
    b = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(("--%s\r\n" % b).encode())
        out.append(('Content-Disposition: form-data; name="%s"\r\n\r\n' % k).encode())
        out.append((str(v) + "\r\n").encode())
    out.append(("--%s\r\n" % b).encode())
    out.append(('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % filename).encode())
    out.append(b"Content-Type: image/jpeg\r\n\r\n")
    out.append(filebytes)
    out.append(("\r\n--%s--\r\n" % b).encode())
    body = b"".join(out)
    h = {"Authorization": key,
         "Content-Type": "multipart/form-data; boundary=" + b}
    r = urllib.request.Request(BASE + path, data=body, method="POST", headers=h)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")
    except Exception as e:
        return None, "ERROR: " + str(e)


def first_id(o):
    if isinstance(o, dict):
        if "id" in o:
            return o["id"]
        for v in o.values():
            r = first_id(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = first_id(v)
            if r is not None:
                return r
    return None


def main():
    key = find_key()
    if not key:
        print("Could not find hw_key.txt.")
        print("Create it: open Notepad, paste your Handwrytten key, Save As")
        print(r"  hw_key.txt   in   C:\Users\aaron\clawd-shared")
        return
    H = {"Authorization": key}
    print("Key loaded. Talking to", BASE, "\n")

    print("=== 0. list dimensions ===")
    st, txt = req("/cards/listDimensions", headers=H)
    print("HTTP", st)
    print(txt[:1200], "\n")
    dim_id = 1
    try:
        fid = first_id(json.loads(txt))
        if fid is not None:
            dim_id = int(fid)
    except Exception:
        pass
    print("using dimension_id =", dim_id, "\n")

    print("=== 1. get a placeholder image ===")
    img = None
    for u in IMG_URLS:
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                img = r.read()
            print("downloaded", len(img), "bytes from", u)
            break
        except Exception as e:
            print("failed", u, "-", e)
    if not img:
        print("could not get an image, stopping.")
        return
    print()

    print("=== 2. upload cover ===")
    st, txt = multipart("/cards/uploadCustomLogo", key,
                        {"type": "cover"}, "cover.jpg", img)
    print("HTTP", st)
    print(txt[:1200], "\n")
    cover_id = None
    try:
        cover_id = json.loads(txt).get("id")
    except Exception:
        pass
    print("cover_id =", cover_id, "\n")
    if cover_id is None:
        print("no cover_id -> stopping (see the upload response above).")
        return

    print("=== 3. create custom card ===")
    body = json.dumps({"name": "Reveal Card Test",
                       "dimension_id": dim_id,
                       "cover_id": cover_id}).encode()
    st, txt = req("/cards/createCustomCard", "POST",
                  {**H, "Content-Type": "application/json"}, body)
    print("HTTP", st)
    print(txt[:1200], "\n")
    card_id = None
    try:
        card_id = json.loads(txt).get("id")
    except Exception:
        pass
    print("card_id =", card_id, "\n")
    if card_id is None:
        print("no card_id -> stopping (see the create-card response above).")
        return

    print("=== 4. single-step order (TEST MODE) ===")
    order = {
        "card_id": card_id, "font_label": FONT,
        "message": "Test from the Omni reveal card pipeline. Please ignore.",
        "sender_first_name": SENDER["first"], "sender_last_name": SENDER["last"],
        "sender_address1": SENDER["a1"], "sender_address2": SENDER["a2"],
        "sender_city": SENDER["city"], "sender_state": SENDER["state"], "sender_zip": SENDER["zip"],
        "sender_country": "United States", "sender_country_id": 1,
        "recipient_first_name": RECIP["first"], "recipient_last_name": RECIP["last"],
        "recipient_address1": RECIP["a1"], "recipient_address2": RECIP["a2"],
        "recipient_city": RECIP["city"], "recipient_state": RECIP["state"], "recipient_zip": RECIP["zip"],
        "recipient_country": "United States", "recipient_country_id": 1,
    }
    st, txt = req("/orders/singleStepOrder", "POST",
                  {**H, "Content-Type": "application/json"},
                  json.dumps(order).encode())
    print("HTTP", st)
    print(txt[:2000], "\n")
    print("=== DONE ===")
    print("Send me the HTTP codes and the responses above. A screenshot is fine.")


try:
    main()
except Exception as e:
    print("SCRIPT ERROR:", e)
finally:
    try:
        input("\nPress Enter to close...")
    except Exception:
        pass
