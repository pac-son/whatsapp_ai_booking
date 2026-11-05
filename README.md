# A WhatsApp AI Booking and Customer Assistant for Nigerian and African Diaspora Businesses in the UK

Product concept, market position, MVP scope and technical architecture

## 1. What we are building
We are building a WhatsApp-based AI assistant that runs customer conversations, bookings and orders for small businesses owned by Nigerian and wider African diaspora communities in the UK. Customers message the business on WhatsApp as they already do. The assistant answers in English or Nigerian Pidgin, quotes real prices, checks availability, takes a deposit, and hands the chat to the owner when a human is needed.

It is not a generic FAQ chatbot. It is a workflow product for specific kinds of business: hair braiding and beauty salons first, then African food and grocery shops, event and catering planners, and fashion and tailoring businesses. Customer records and AI processing are hosted in the UK, with UK GDPR compliance built in from the start.

## 2. The problem
Many diaspora business owners run their entire business through WhatsApp, a habit they brought from Nigeria and other African markets, where WhatsApp is the storefront. In the UK this creates familiar problems:
- Messages go unanswered for hours, and customers book with whoever replies first.
- The owner is the only person answering, including evenings and weekends.
- Bookings, deposits and stock are tracked by hand across chat threads.
- Mainstream UK tools are built for generic small businesses, and African-focused tools are built for businesses on the continent, not for owners in the UK.

## 3. Market and competition
| Group | Examples found | Gap for us |
|---|---|---|
| Global WhatsApp platforms | Wati, Respond.io, Gallabox, Yellow.ai, SleekFlow, Twilio | Horizontal products with no cultural or community focus, mostly not UK-hosted by positioning |
| Africa-focused tools | JamiiBot (Tanzania), ChatBots Africa (Ghana), ChatDaddy's Nigeria push | Built for businesses in Africa, not for diaspora owners operating under UK rules and payment systems |
| Freelance bot builders | Fiverr and similar gig listings | One-off custom bots, no product, no support, no compliance story |
| Meta Business Agent | Free AI agent in the WhatsApp Business app, announced June 2026 | Covers basic AI replies. Free usage is limited and language support is not universal |

I found no platform built specifically for African diaspora businesses in the UK. This is based on the searches run during this research and is not proof that none exists, so it should be re-checked before launch.

## 4. Positioning and differentiation
Meta now gives away basic AI replies inside WhatsApp, so AI answering questions is not the product. The product is the layer Meta does not provide:
- Workflows that finish jobs: bookings with availability rules, deposits, stock checks, quotes and group orders.
- Language and culture: Nigerian Pidgin from day one, then Yoruba and Igbo, and voice-note handling in Phase 2.
- UK data story: customer records and AI processing hosted in the UK, worded carefully (see section 8).
- Human handoff done well: the owner is alerted and can take over the chat in one tap.
- Community-native distribution through diaspora business groups, church networks and community events.

## 5. Target customers
| Vertical | Core workflow to automate |
|---|---|
| Hair braiding and beauty salons (first) | Service and duration booking, deposit collection, reminders, no-show reduction |
| African food and grocery shops | Pre-orders for imported items, stock checks, pickup and delivery slots |
| Event and catering planners | Quote requests, guest count, date availability, deposits |
| Fashion and tailoring | Order status, fitting appointments, group orders such as aso-ebi |

## 6. MVP scope
| Phase | Scope |
|---|---|
| Phase 1 (weeks 1-8) | One vertical (salons). WhatsApp connection via Cloud API; AI replies grounded in the business's services, prices and hours; booking flow with deposit link (Stripe); human handoff; simple owner dashboard; English and Pidgin. |
| Phase 2 (months 3-5) | Voice-note transcription; Yoruba and Igbo; food/grocery and event/catering verticals; reminders and no-show reduction. |
| Phase 3 (after paying customers) | Group-order coordination; review requests; consent-based broadcast campaigns; Xero and calendar integrations; other diaspora communities. |

Before writing code, speak to 10 to 15 target businesses and offer a free 30-day pilot to 3 to 5 of them. If salons will not use it, that should be learned before months of building.

## 7. Technical architecture
| Stage | What it does |
|---|---|
| 1. Customer on WhatsApp | Customers send text or voice notes in English or Pidgin. |
| 2. Meta WhatsApp Cloud API | Official route into WhatsApp, delivering messages to us by webhook. Uses "WhatsApp Coexistence" to allow the business to keep their existing WhatsApp Business app and phone number alongside the API. |
| 3. UK-hosted message gateway | Receives webhooks, queues messages, records consent, keeps audit logs and supports deletion requests. Hosted in a UK region. |
| 4. AI conversation engine | Google Cloud Vertex AI (Gemini 1.5 Flash) plus tools: check availability, create booking, create payment link, look up price, check stock, hand off to owner. Each business has its own knowledge base. |
| 5. Owner dashboard and handoff | Mobile-first web app showing bookings, conversations needing attention and one-tap takeover. |

**Suggested stack**
- Backend: Python with FastAPI, or TypeScript with Node
- Database: PostgreSQL in a UK region
- Queue: SQS or Redis
- Payments: Stripe payment links and deposits
- Voice notes (Phase 2): a speech-to-text model, tested on real Nigerian-accented English and Pidgin recordings
- Dashboard: React or Next.js
- Hosting: AWS London or Azure UK South

## 8. Compliance and data notes
- UK GDPR: record consent, set a retention policy, support deletion requests, and sign data processing agreements with each vendor.
- Data residency claim: messages still pass through Meta, so the accurate claim is that customer records and AI processing are hosted in the UK, not that data never touches Meta.
- LLM location: **Resolved.** We will use Google Cloud Vertex AI pinned to the `europe-west2` (London) region to guarantee all AI processing and data at rest remains strictly in the UK, satisfying UK GDPR requirements.
- AI disclosure: tell customers at the start of a chat that they are speaking with an AI assistant.
- Meta policy: since January 2026 AI agents on WhatsApp must be task-specific, not general-purpose. Design each bot around a defined business function.

## 9. Pricing hypothesis and validation
A flat monthly fee for small owners, roughly 30 to 80 pounds depending on features, with Meta's per-message charges either included or shown clearly. This is a hypothesis to test in pilots, not a finding. Check Meta's current UK rate card before fixing margins.

## 10. Key risks
- Meta's free Business Agent may be good enough for simple salons. Mitigation: compete on deposits, multi-step bookings, language quality and handoff, and confirm this in pilots.
- The niche is smaller than the general UK small-business market. Mitigation: use easier distribution as the beachhead, then extend to other diaspora communities.
- Voice-note and Pidgin accuracy is unproven. Mitigation: test on real recordings before promising it.
- Owners may resist changing their WhatsApp number. **Mitigation: Not an issue.** Meta's "WhatsApp Coexistence" feature allows owners to keep their existing WhatsApp Business app and number while using the Cloud API.

## 11. Next steps
- Interview 10 to 15 diaspora business owners, starting with salons.
- ~~Confirm Cloud API onboarding and number coexistence options.~~ (Confirmed: WhatsApp Coexistence is supported for Business App v2.24.17+).
- ~~Check UK or EU processing options with LLM providers.~~ (Resolved: Using Vertex AI in London).
- Build the Phase 1 booking flow and run 3 to 5 free pilots.
- Decide on pricing and the second vertical based on pilot results.
