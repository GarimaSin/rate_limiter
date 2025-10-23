-- token_bucket.lua
local key = KEYS[1]
local now = tonumber(ARGV[1])
local rate_per_sec = tonumber(ARGV[2])
local burst = tonumber(ARGV[3])
local consume = tonumber(ARGV[4])
local ttl_ms = tonumber(ARGV[5])

local data = redis.call("HMGET", key, "tokens", "last_ts")
local tokens = tonumber(data[1])
local last_ts = tonumber(data[2])

if tokens == nil or last_ts == nil then
  tokens = burst
  last_ts = now
end

local elapsed_ms = math.max(0, now - last_ts)
local refill_tokens = (elapsed_ms / 1000.0) * rate_per_sec
tokens = math.min(burst, tokens + refill_tokens)
last_ts = now

local allowed = 0
local retry_after_ms = 0

if tokens >= consume then
  tokens = tokens - consume
  allowed = 1
else
  local needed = consume - tokens
  if rate_per_sec > 0 then
    retry_after_ms = math.ceil((needed / rate_per_sec) * 1000.0)
  else
    retry_after_ms = 0
  end
end

redis.call("HMSET", key, "tokens", tostring(tokens), "last_ts", tostring(last_ts))
redis.call("PEXPIRE", key, ttl_ms)
return { tostring(allowed), tostring(math.floor(tokens)), tostring(retry_after_ms) }
