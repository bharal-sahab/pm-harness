# Story splitting patterns

Use these when a story is too big to finish in a few days, has more than about six
acceptance criteria, or mixes unrelated behaviors. Each split must still deliver
something observable.

| Pattern | Split by | Example |
|---------|----------|---------|
| Workflow steps | Each step of a journey | "Request a return" / "Receive a return" / "Refund a return" |
| Happy and unhappy paths | Success first, then each failure | "Apply a valid code" / "Explain an expired code" / "Explain a used-up code" |
| Business rule variations | One rule or variant at a time | "Percentage discounts" / "Fixed amount" / "Buy X get Y" |
| Data variations | Simple data first | "One currency" / "Multiple currencies" |
| Interfaces | One surface at a time, when they can ship separately | "Store API returns the reason" / "Storefront shows it" / "Admin report" |
| Roles | One user type at a time | "Shopper sees it" / "Support agent sees it" |
| Simple then complete | A minimal version, then enhancements | "Generic message" / "Specific message per reason" |
| Defer quality attributes | Make it work, then make it fast or scale | "Works for 100 items" / "Works for 10,000 items" |
| Spike | Investigate the unknown first, time-boxed | "Spike: can old mobile apps ignore the new field?" |

## Signs a story is too big

- The title contains "and" or "manage".
- It touches more than two surfaces that different people build.
- The team cannot agree on an estimate, or the estimate is the largest size they use.
- It has acceptance criteria for several user types.

## Signs a split went wrong

- A story only makes sense once another one ships, and neither is visible alone
  (horizontal slices: "backend" / "frontend"). Combine them, or make the first one
  observable through the API.
- A story has no user, operator, or API consumer who would notice it is done.
