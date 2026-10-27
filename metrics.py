from prometheus_client import start_http_server, Gauge, Counter, Histogram

BOT_READY = Gauge("sina_chan_ready", "1 if the bot is ready, 0 otherwise")
BOT_GUILD_COUNT = Gauge("sina_chan_guild_count", "Number of guilds the bot is in")
BOT_LATENCY_SECONDS = Gauge("sina_chan_latency_seconds", "Discord gateway latency")
BOT_SHARD_COUNT = Gauge("sina_chan_shard_count", "Number of shards")

BOT_COMMANDS_TOTAL = Counter(
    "sina_chan_commands_total",
    "Number of commands that completed successfully",
    ["command", "type"],
)
BOT_COMMAND_ERRORS_TOTAL = Counter(
    "sina_chan_command_errors_total",
    "Number of commands that ended in an error",
    ["command", "type", "error_type"],
)
BOT_COMMAND_LATENCY_SECONDS = Histogram(
    "sina_chan_command_latency_seconds",
    "Command execution time in seconds, from invocation to successful completion",
    ["command", "type"],
)


def start_metrics_server(port: int = 9200) -> None:
    # ループバック限定。既存のmysqld_exporter・blackbox_exporterと同じ考え方で、
    # 同一ホスト上のAlloyだけがスクレイプできればよい
    start_http_server(port, addr="127.0.0.1")
