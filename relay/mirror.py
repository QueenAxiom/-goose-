"""Read-only local mirror of our own sites into sites/<domain>/mirror/. Stdlib only."""
import re, sys, time, urllib.request, urllib.parse, pathlib, collections

MAX_PAGES, MAX_ASSETS, DELAY = 40, 400, 0.15
UA = {"User-Agent": "Axiom-local-mirror/1.0"}

def get(url):
    """Fetch with curl (uses the Windows cert store; Python's bundle lacks some chains)."""
    import subprocess, tempfile, os
    fd, tmp = tempfile.mkstemp(); os.close(fd)
    try:
        r = subprocess.run(["curl", "-s", "-L", "-m", "25", "-A", UA["User-Agent"], "-o", tmp,
                            "-w", "%{http_code} %{content_type}", url], capture_output=True, text=True)
        code, _, ctype = r.stdout.partition(" ")
        if code != "200":
            print("  skip", url, code); return None, None
        return open(tmp, "rb").read(), ctype.split(";")[0].strip().lower()
    except Exception as e:
        print("  skip", url, type(e).__name__); return None, None
    finally:
        os.unlink(tmp)

def local_path(root, url, ctype):
    p = urllib.parse.urlparse(url).path or "/"
    if ctype == "text/html" and not re.search(r"\.[a-z0-9]{2,5}$", p):
        p = p.rstrip("/") + "/index.html"
    return root / p.lstrip("/")

def mirror(domain):
    base = f"https://{domain}"
    root = pathlib.Path("sites") / domain / "mirror"
    prefix = f"/sites/{domain}/mirror"
    seen, queue, pages, assets = set(), collections.deque([base + "/"]), 0, 0
    sm, _ = get(base + "/wp-sitemap.xml")
    if sm:
        for u in re.findall(rb"<loc>([^<]+)</loc>", sm):
            u = u.decode()
            if u.endswith(".xml"):
                sub, _ = get(u)
                queue.extend(x.decode() for x in re.findall(rb"<loc>([^<]+)</loc>", sub or b""))
            else:
                queue.append(u)
    host_re = re.compile(r"https?:(?:\?/\?/)(?:www\.)?" + re.escape(domain))
    while queue:
        url = queue.popleft().split("#")[0]
        if url in seen or urllib.parse.urlparse(url).netloc.replace("www.", "") != domain:
            continue
        if re.search(r"/(wp-json|xmlrpc\.php|wp-admin|wp-login|feed|oembed)|[?&](rest_route|p|replytocom|add-to-cart|remove_item|add_to_wishlist)=", url):
            continue
        seen.add(url)
        body, ctype = get(url)
        if body is None:
            continue
        is_page = ctype == "text/html"
        if is_page and pages >= MAX_PAGES or not is_page and assets >= MAX_ASSETS:
            continue
        pages += is_page; assets += not is_page
        dest = local_path(root, url, ctype)
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        if ctype in ("text/html", "text/css", "application/javascript", "text/javascript", "application/json"):
            text = body.decode("utf-8", "replace")
            for m in re.findall(r"""(?:href|src)=["']([^"']+)["']|url\(["']?([^)"']+)""", text):
                ref = urllib.parse.urljoin(url, m[0] or m[1]).split("#")[0]
                if urllib.parse.urlparse(ref).netloc.replace("www.", "") == domain:
                    queue.append(ref)
            text = host_re.sub(prefix, text)
            try:
                dest.write_text(text, encoding="utf-8")
            except OSError:
                continue
        else:
            try:
                dest.write_bytes(body)
            except OSError:
                continue
        time.sleep(DELAY)
    print(f"{domain}: {pages} pages, {assets} assets -> {root}")

for d in sys.argv[1:]:
    mirror(d)
