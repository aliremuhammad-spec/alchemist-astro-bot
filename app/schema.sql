-- Idempotent schema; applied on every boot.
CREATE TABLE IF NOT EXISTS users (
  id            BIGINT PRIMARY KEY,           -- Telegram user id
  first_name    TEXT,
  username      TEXT,
  lang          TEXT NOT NULL DEFAULT 'ar',
  tz            TEXT,                          -- current timezone (for daily delivery)
  start_param   TEXT,                          -- where they came from
  blocked       BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS profiles (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL,
  birth_date  DATE NOT NULL,
  birth_time  TIME,                            -- NULL = unknown
  city_id     BIGINT,
  city        TEXT,
  country     TEXT,
  lat         DOUBLE PRECISION NOT NULL,
  lng         DOUBLE PRECISION NOT NULL,
  tz          TEXT NOT NULL,
  indian_style TEXT NOT NULL DEFAULT 'north',
  is_main     BOOLEAN NOT NULL DEFAULT FALSE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS profiles_user ON profiles(user_id);

CREATE TABLE IF NOT EXISTS daily_prefs (
  user_id     BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  subscribed  BOOLEAN NOT NULL DEFAULT TRUE,
  send_time   TEXT NOT NULL DEFAULT '08:00',   -- HH:MM in tz
  tz          TEXT NOT NULL,
  sign        INT NOT NULL,                    -- 0..11
  last_sent   DATE
);

-- Channels and groups that receive the daily horoscope digest.
CREATE TABLE IF NOT EXISTS broadcast_chats (
  chat_id     BIGINT PRIMARY KEY,
  title       TEXT,
  kind        TEXT,                            -- channel | group | supergroup
  added_by    BIGINT,
  active      BOOLEAN NOT NULL DEFAULT TRUE,
  send_time   TEXT NOT NULL DEFAULT '09:00',
  tz          TEXT NOT NULL,
  lang        TEXT NOT NULL DEFAULT 'ar',
  last_sent   DATE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content_daily (
  day        DATE PRIMARY KEY,
  data       JSONB NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS content_weekly (
  week_start DATE PRIMARY KEY,
  data       JSONB NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feedback (
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT,
  text       TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscriptions (       -- premium (Stars or manual)
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  source      TEXT NOT NULL,                     -- stars | manual
  starts_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  ends_at     TIMESTAMPTZ NOT NULL,
  charge_id   TEXT,
  granted_by  BIGINT,
  note        TEXT
);
CREATE INDEX IF NOT EXISTS subs_user ON subscriptions(user_id, ends_at);

CREATE TABLE IF NOT EXISTS ad_events (            -- ready for rewarded ads
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT,
  provider   TEXT NOT NULL,
  placement  TEXT NOT NULL,
  status     TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events (               -- light analytics
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT,
  name       TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS kv (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- One-time tickets: an ad view (or a no-fill fallback) unlocks one synastry.
CREATE TABLE IF NOT EXISTS ad_tickets (
  id          TEXT PRIMARY KEY,
  user_id     BIGINT NOT NULL,
  placement   TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  provider    TEXT,
  used_at     TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ad_tickets_user ON ad_tickets(user_id, created_at);

CREATE TABLE IF NOT EXISTS payments (
  id           BIGSERIAL PRIMARY KEY,
  user_id      BIGINT NOT NULL,
  stars        INT NOT NULL,
  charge_id    TEXT UNIQUE,
  payload      TEXT,
  recurring    BOOLEAN,
  first_recurring BOOLEAN,
  expires_at   TIMESTAMPTZ,
  refunded     BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- referrals (personal invites) and per-user credits
ALTER TABLE users ADD COLUMN IF NOT EXISTS report_credits INT NOT NULL DEFAULT 0;      -- free natal reports (invite gift)
ALTER TABLE users ADD COLUMN IF NOT EXISTS syn_report_credits INT NOT NULL DEFAULT 0;  -- paid synastry reports
CREATE TABLE IF NOT EXISTS referrals (
  invitee_id    BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  inviter_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  activated_at  TIMESTAMPTZ,
  reward_days   INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS referrals_inviter ON referrals(inviter_id);
CREATE TABLE IF NOT EXISTS report_log (
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT NOT NULL,
  kind       TEXT NOT NULL,                  -- natal | synastry
  paid_with  TEXT NOT NULL,                  -- premium | credit | admin
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS report_log_user ON report_log(user_id, kind, created_at);
ALTER TABLE broadcast_chats ADD COLUMN IF NOT EXISTS ref_link TEXT;                  -- owner's Telegram affiliate link
