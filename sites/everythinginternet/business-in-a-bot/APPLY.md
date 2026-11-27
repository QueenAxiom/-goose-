# Apply: Business in a Bot page (GoDaddy / WordPress)

**Not live.** Nothing here changes production until someone pastes it in WordPress. Do not install, remove, or update plugins.

## Files

| File | What it is |
|------|------------|
| `page.html` | The whole page as WordPress block code: a Custom HTML block, a Jetpack form, then a closing Custom HTML block. |
| `media/business-in-a-bot-medium.mp4` | Demo video: "Medium" cut, 21.6 s, 1080×1920, 3.7 MB. |
| `media/business-in-a-bot-poster.webp` | Video poster (frame at 3 s), 720×1280. |

## Why a Page, not a WooCommerce product

The site has **no subscriptions plugin**, so the $197/month trial can't check out. Per the owner's ruling, every button goes to the application form until one is installed. No fake checkout. With nothing to add to the cart yet, this is a normal WordPress Page.

## Steps

1. **Media → Add New:** upload both files from `media/`. Copy each file's URL.
2. **Check Jetpack Forms is on:** Jetpack → Settings → Writing → Forms (or Jetpack → Modules → Forms). Turn it on if it's off. This turns on a feature of the installed Jetpack plugin; it does not install anything.
3. **Pages → Add New.** Title: `Business in a Bot`. Slug: `business-in-a-bot`.
4. Open the **⋮ menu → Code editor**. Paste the full contents of `page.html`.
5. In the pasted code, replace:
   - `VIDEO_URL` with the `.mp4` URL from step 1
   - `POSTER_URL` with the `.webp` URL from step 1
6. Switch back to the Visual editor. You should see:
   - a Custom HTML block
   - a Group holding a Shortcode block with the `[contact-form]` code
   - a second Custom HTML block
7. In page settings, pick the **full-width / no title** template if the theme has one. The page also hides the theme header and title through the existing Additional CSS (`body:has(.ei-shell)`).
8. **Save as draft. Preview. Do not publish until the owner approves.**

## Where applications go

Jetpack Forms emails each entry to the site admin email. Entries are also kept under **Feedback** in wp-admin. To send them to a different address, add `to="address@example.com"` inside `[contact-form ...]`.

## Verify in preview

- Hero shows the headline, the trial button, and the video with its poster. The video plays.
- Prices read exactly: $197/month with 14-day trial, $30,000, $45,000, 2% royalty. "All prices in CAD, GST included." appears.
- Each door button jumps to the form and pre-picks that door.
- The form sends and shows Jetpack's thank-you message, and the entry arrives by email or under Feedback.
- At phone width (about 390 px): nav shows the brand and Apply, the four doors stack with Monthly first, and nothing scrolls sideways.
- Shop, cart, checkout, and My Account are unchanged.

## Open items

- **Captions:** the video has narration but no captions file. A `.vtt` file should be added for viewers who can't hear it.
- **Later:** once a subscriptions plugin is installed, the trial button can go to a real product checkout instead of the form.
