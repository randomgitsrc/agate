# Agateon brand assets

The mark reads two ways at once: an "A" for Agateon, and a gate — two posts with a crossbar. The teal band across the crossbar is a checkmark cut into the gate itself: nothing passes until it's checked.

## Files

| File | Use it for |
|---|---|
| `logo-mark.svg` | Icon alone, light backgrounds. Docs headers, in-line references. |
| `logo-mark-dark-bg.svg` | Icon alone, dark backgrounds. |
| `favicon-mark.svg` / `favicon-16.png` / `favicon-32.png` | Browser tab icon. Simplified — no checkmark detail, it disappears below ~40px anyway. |
| `apple-touch-icon-180.png` | iOS/Android home-screen icon. |
| `logo-lockup.svg` | Icon + wordmark, light backgrounds. README header, docs site header. |
| `logo-lockup-dark-bg.svg` | Icon + wordmark, dark backgrounds. |
| `avatar.svg` / `avatar.png` | GitHub org avatar, social profile pictures. Filled square, survives circular cropping. |
| `social-preview.png` | GitHub repo social preview image (Settings → Social preview). Shown when the repo link is shared on social media, Slack, etc. |
| `logo-mark.png` | Raster fallback of the icon for contexts that don't accept SVG. |
| `color-palette.svg` | Reference sheet, hex values below. |

## Using the light/dark pair in a README

GitHub respects `prefers-color-scheme` inside a `<picture>` element in README markdown:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/brand/logo-lockup-dark-bg.svg">
  <img alt="Agateon" src="docs/brand/logo-lockup.svg">
</picture>
```

## Color

| Name | Hex | Use |
|---|---|---|
| Ink | `#1A1A18` | Text, structure, primary mark on light backgrounds |
| Paper | `#FAF9F4` | Light background, primary mark on dark backgrounds |
| Gate teal | `#1D9E75` | Pass, fix, verified |
| Blocked coral | `#D85A30` | Caught failure, blocked state |
| Agent purple | `#7F77DD` | The agent being verified — use sparingly, only when depicting an agent as an actor |

## Rules

- Don't recolor the mark outside this palette.
- Don't stretch — the icon and lockup are fixed-ratio.
- Keep clear space around the mark equal to at least the width of one gate post.
- Don't add drop shadows, gradients, or outlines to the mark itself.
- The checkmark-in-crossbar detail is load-bearing at large sizes and irrelevant at small ones — use `favicon-mark.svg` below ~40px, not a shrunk `logo-mark.svg`.
