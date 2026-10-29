# EverythingInternet.ca — founding funnel redesign

Paste-ready WordPress / GoDaddy snippets for the EverythingInternet.ca founding-funnel redesign (Lifetime Directory Listing). These snippets do not name a price.

These files are **not live**. Production WordPress is unchanged until someone pastes them in the GoDaddy / WordPress editor. Follow `APPLY.md` for where each snippet goes. Do not install plugins or deploy from this folder.

| File | Paste target |
|------|----------------|
| `additional-css.css` | Appearance → Customize → Additional CSS (append) |
| `homepage.html` | Pages → Home (id 50) → Custom HTML (replace page content) |
| `product-pricing-card.html` | Products → Lifetime Directory Listing → Short description |
| `product-description.html` | Same product → Description (long) |
| `directory-sample.html` | Pages → Add New → title “Sample Directory”, slug `sample-directory`, Custom HTML |
| `APPLY.md` | Apply notes for the person pasting into WordPress (do not paste this file into a page) |

## Images

There are **no image files** in this folder and **no `<img>` tags** in the HTML. Company cards are text links. Do not add stock photos or fake company photos.

When a real asset is added later, convert it to WebP at quality 75–80 and use this markup:

```html
<!-- Hero / LCP, above the fold: never lazy-load -->
<img src="images/hero.webp" alt="..." width="1120" height="630" fetchpriority="high" decoding="async">

<!-- Everything below the fold -->
<img src="images/example.webp" alt="..." width="240" height="160" loading="lazy" decoding="async">
```

`width` and `height` must be the file’s pixel size. Only the hero / LCP image gets `fetchpriority="high"`, and that image must not set `loading="lazy"`.
