# Optional upgrade: cloud accounts via Supabase (free tier)

**Current baseline (decided): progress stays per-device in `localStorage` — free, zero
GDPR exposure. This file is the 30-minute on-ramp if/when you want cross-device sync.**

## Why Supabase (and the settings that matter)

- Free tier covers this project's scale comfortably (hundreds of thousands of checklist saves)
- **Choose region `eu-central-1` (Frankfurt) at project creation** — data stays in the EU
- **Email magic links** instead of passwords = less liability, nothing to leak
- Open source + standard Postgres: no lock-in drama

## 1. Database (SQL editor → run once)

```sql
create table public.progress (
  user_id    uuid primary key references auth.users on delete cascade,
  checked    jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.progress enable row level security;   -- users see ONLY their own row

create policy "own row only" on public.progress
  for all using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

## 2. Wire it into index.html (production mode)

Add before `</body>` (replace the two config strings):

```html
<script type="module">
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";
const sb = createClient("https://YOUR-PROJECT.supabase.co", "YOUR-ANON-KEY");

// login button → magic link:
async function signIn(email){ await sb.auth.signInWithOtp({ email }); }

// after loadChecks(): hydrate cloud progress → localStorage
const { data: { user } } = await sb.auth.getUser();
if (user) {
  const { data } = await sb.from("progress").select("checked").single();
  if (data) localStorage.setItem("wm-checklist-v1", JSON.stringify(data.checked));
}

// inside the checkbox change handler, after saving to localStorage:
if (user) {
  const saved = JSON.parse(localStorage.getItem("wm-checklist-v1") || "{}");
  await sb.from("progress").upsert({ user_id: user.id, checked: saved, updated_at: new Date() });
}
</script>
```

## 3. GDPR checklist the day you switch it on

- [ ] Privacy notice linked in footer (what: email + checklist state; why; retention)
- [ ] Region confirmed: EU (Frankfurt)
- [ ] Anonymous local-only mode still offered (it's already the default)
- [ ] Deletion path documented: `delete from auth.users …` on request
- [ ] Update the footer GDPR line in index.html
