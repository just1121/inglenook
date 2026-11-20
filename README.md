# Inglenook flipbook

A self-contained page-turning viewer for the Inglenook brochure. One HTML file plus page images. No outside services, no libraries, no tracking.

## Preview locally

Double-click `index.html`. It works straight from the folder.

## Put it on GitHub Pages

1. Push this folder's contents to the root of the repo, branch `main`.
2. On GitHub, open the repo, then Settings > Pages.
3. Under "Build and deployment", set Source to "Deploy from a branch".
4. Set Branch to `main` and folder to `/ (root)`. Click Save.
5. After a minute or two the site is at `https://<user>.github.io/<repo>/`.

## Put it on another site

Copy the whole folder to any web server and link to it, or embed it:

```html
<iframe src="/path/to/flipbook/" title="Inglenook brochure"
        style="width:100%;aspect-ratio:16/9;border:0" allowfullscreen></iframe>
```

## Update from a new PDF

```
python3 tools/build.py /path/to/new.pdf
```

This re-renders `pages/` and rewrites `pages/manifest.js`. It needs Poppler (`brew install poppler` on a Mac) and works best with Pillow (`pip3 install pillow`). It never touches `book.js`.

Add `--single-file out.html` to also write a one-file version with the images inlined, handy for previewing or emailing.

## book.js

Hand-edited content: the tab title, alt text for each page, a hidden transcript of each page's copy for screen readers, and the clickable areas on the contact line. If the copy in the PDF changes, update the matching transcript here. If pages are added or removed, add or remove entries to match.

## Staging note

`index.html` carries `<meta name="robots" content="noindex, nofollow">` so search engines skip this staging copy. Remove that line when it goes live.

## Controls

- Click or drag a page, swipe, or use the arrows at the sides.
- Keyboard: Left/Right, PageUp/PageDown, Home/End, Space and Shift+Space. F for fullscreen. Esc leaves zoom or closes the thumbnails.
- Bottom bar: thumbnails, page number, single/spread view, zoom, fullscreen.
- Link straight to a page with `#p=4` on the end of the address.
