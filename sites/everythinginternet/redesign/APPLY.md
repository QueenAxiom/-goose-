# Apply EverythingInternet.ca redesign (GoDaddy / WordPress)

## Status from executor
- Live production still shows old homepage (narrow red card, fake companies like Maple Grove Foods).
- Product page already has $499 / ~~$2,999~~ and improved copy, but still default Woo layout / widgets / faded graphic.
- Staging `1246975.us8.myftpupload.com` **redirects to production** — no separate staging path.
- Executor had **no Vault tool** and **no browser/computerUse tool** — cannot sign into GoDaddy/WP. Parent must dispatch browser with Alan's GoDaddy or WP login.

## Keep live
- Lifetime Directory Listing product: sale **$499**, regular **$2,999**, purchasable.
- Founding “Only 10 Spots” / “X of 10 founding spots left” (files ship with **10 of 10**).
- Monthly listing link stays.

## Files
| File | Where to paste |
|------|----------------|
| `additional-css.css` | Appearance → Customize → Additional CSS (append) |
| `homepage.html` | Pages → Home (id 50) → replace content with Custom HTML |
| `product-pricing-card.html` | Products → Lifetime Directory Listing → Short description |
| `product-description.html` | Same product → Description (long) |
| `directory-sample.html` | Pages → Add New → title “Sample Directory”, slug `sample-directory`, Custom HTML, Publish |

## Images

This package ships **no image files**. `APPLY.md` does not point at any asset to upload. Do not add stock or fake company photos. The product featured image (faded promo graphic) should be removed, not replaced.

If a real logo or photo is added later: WebP at quality 75–80, `width` and `height` set to the file’s pixel size, `loading="lazy"` below the fold. The hero / LCP image gets `fetchpriority="high"` and must not be lazy-loaded.

## Product cleanup (no plugins)
1. Edit product → remove / unset Featured image (faded promo graphic).
2. In product page template / widgets: leave plugins alone; Additional CSS hides recent posts/comments, gallery, related, tabs.
3. Confirm Add to cart still shows Woo price $499.

## Verify
- Home: sticky navy nav, full-width hero, **10 of 10 founding spots left**, real Canadian companies, working Sample directory link.
- `/product/lifetime-directory-listing/`: pricing card matches home messaging; no fake widgets; $499 intact; checkout still works.
- `/sample-directory/`: sample board loads (fixes old `#` View sample).
- No call/phone button added.
- Do not install/remove/update/deactivate plugins; no mu-plugins; no deploy backups.

## Login needed
Parent: open GoDaddy Managed WordPress for everythinginternet.ca (prefer GoDaddy UI) or `https://everythinginternet.ca/wp-admin/`, fill Vault login if present, else RequestUserForm for GoDaddy/WP. Then apply files above and screenshot home + product + sample-directory.
