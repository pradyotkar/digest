# Pradykar.com Redesign

## Status
- Branch: `redesign/pradykar-professional-v2`
- Base: `71bc867` (previous multi-page version)
- Backup: `backup/pre-redesign-2026-07-18`

## Files Changed
| File | Change | Status |
|------|--------|--------|
| index.html | Full redesign: new hero, expertise cards, timeline, credibility strip, CTA section, Labs section | ✅ |
| experience.html | NEW — Detailed Visa/Bayshore career narrative | ✅ |
| labs.html | NEW — Automated research, experiments, personal projects | ✅ |
| about.html | NEW — About page with corrected Visa tenure wording | ✅ |
| contact.html | NEW — Contact page with email, LinkedIn, Bayshore links | ✅ |
| travel.html | Cleaned — Removed unfinished content, noindex | ✅ |
| _redirects | Updated — /bayshore-visa → /experience 301 | ✅ |
| docs/WEBSITE_UPGRADE.md | NEW — Progress tracking | ✅ |

## Changes Implemented

### Phase 1: Audit
- Repository structure inspected: static HTML, Cloudflare Pages, GitHub deploy
- Source files identified (no generator — hand-coded HTML)
- Working branch created: `redesign/pradykar-professional-v2`

### Phase 2: Credibility
- Visa tenure wording corrected: `"24 years working on Visa payment infrastructure, including more than 13 years as a Visa employee"`
- Removed unsupported `"every Visa transaction worldwide"` — replaced with accurate `"Helped lead testing, reliability, and release certification for Visa's core global payment authorization platform"`
- Metrics preserved with proper context (`~50K`, `approximately`, `high-availability operating environment`)
- Unfinished content removed from public pages: "Photos coming soon", "Writeup pending", "Coming soon" badges, developer comments, placeholder cards

### Phase 3: Information Architecture
- New route structure: `/`, `/experience`, `/labs`, `/about`, `/contact`
- Travel under Labs (not primary nav), noindex until content is ready
- /bayshore-visa permanently redirects (301) to /experience
- MarketPulse and Daily Digest remain accessible under Labs

### Phase 4: Visual Design
- Implemented specified design tokens (--ink, --navy, --blue, --gold, --slate, --muted, --border, --surface)
- Inter font throughout, Source Serif for body text on About page
- Clean white/light background, restrained blue accent palette
- No neon, gradients, glassmorphism, or AI imagery
- Professional executive feel with clear hierarchy

### Phase 5: Homepage
- Header with wordmark and "Discuss a Project" CTA in nav
- Hero: eyebrow, headline, supporting text, two CTAs
- Credibility strip: 24 years, 13+ at Visa, ~50K TPS, 99.9999% uptime
- 6 expertise cards (business outcomes, not just technologies)
- 3 selected-work case studies (payment reliability, enterprise AI, compliance advisory)
- Timeline preview → link to full Experience page
- Insights & Labs section (labeled automated/experimental)
- Final CTA with two buttons

### Phase 6: Automated Content (generators unchanged — static site)
- Daily Digest and MarketPulse remain as generated content
- MarketPulse clearly labeled Paused with disclaimer

### Phase 7: SEO
- All pages have unique title, meta description, og:title, og:description, og:url
- Twitter card meta tags on all pages
- travel.html has noindex until content is ready

### Phase 8: Accessibility
- prefers-reduced-motion support on all pages
- Semantic HTML landmarks throughout
- Descriptive link text
- Sufficient color contrast (dark text on light backgrounds)

### Phase 9: Testing
- [ ] Run link checker
- [ ] Validate structured data
- [ ] Check Lighthouse scores

### Phase 10: Deployment
- [ ] Push working branch
- [ ] Verify Cloudflare preview
- [ ] Merge when approved

## Rollback
```bash
git checkout main
git reset --hard backup/pre-redesign-2026-07-18
git push --force origin main
```
