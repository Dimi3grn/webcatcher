from signal_parser import test_parser

# Example signals similar to what you mentioned
test_messages = [
    "#XAUUSD sell now @3257 tp @3247 tp2 @3232 Sl @3265",
    "XAUUSD SEL LIMIT @3237.5 tp @3229 Sl @3240",
    "XAUUSD sell now @ 3249 tp @ 3235 tp 2 @ 3202 SL @ 3257",
    "Just checking the market, no trades yet",
    "Market update: EURUSD is looking bullish",  # Not a signal
    "EURUSD BUY entry 1.0850 SL 1.0820 TP 1.0880",
    "#EURJPY SELL @ 158.240 SL 158.750 TP 157.500 TP2 156.750",
    "USDJPY buy now @156.45 SL @155.98 TP @156.80",
    "BUY GBPJPY @ 182.75 SL @ 182.15 TP @ 183.45",
    "EURUSD approaching support level, watch closely",  # Not a signal
    "Entry 1.2345 Sl 1.2360 Tp 1.2420 GBPUSD Buy"  # Challenging format
]

print("Testing signal parser with sample messages...\n")
test_parser(test_messages)