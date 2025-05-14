import re
from typing import Dict, Any, Tuple, Optional, List
import json

# Regex patterns for identifying trading signals
SYMBOL_PATTERN = r'[#]?(\w+(?:/\w+)?)'  # Matches symbols like EURUSD, XAUUSD, BTC/USD, etc.
DIRECTION_PATTERN = r'(buy|sell|BUY|SELL|Buy|Sell|SEL|LONG|SHORT|Long|Short)'
PRICE_PATTERN = r'[@]?\s*(\d+\.?\d*)'  # Matches prices with @ symbol or without

def is_trading_signal(text: str) -> bool:
    """
    Check if a message is likely a trading signal.
    Returns True if it contains a symbol and a direction (buy/sell).
    """
    # Look for symbol and direction
    symbol_match = re.search(SYMBOL_PATTERN, text)
    direction_match = re.search(DIRECTION_PATTERN, text, re.IGNORECASE)
    
    # Look for price indicators (entry, tp, sl)
    price_indicators = ['@', 'entry', 'tp', 'sl', 'stop', 'target', 'limit']
    has_price_indicator = any(indicator in text.lower() for indicator in price_indicators)
    
    # If we have both a symbol and direction, and some price indicator, it's likely a signal
    return bool(symbol_match and direction_match and has_price_indicator)

def parse_signal(text: str) -> Dict[str, Any]:
    """
    Parse a trading signal message into structured data.
    Returns a dictionary with parsed values.
    """
    # Default result with all fields as None
    result = {
        'symbol': None,
        'direction': None,
        'entry': None,
        'tp1': None,
        'tp2': None,
        'sl': None,
        'confidence': 0.0  # How confident we are in the parsing
    }
    
    # Extract symbol (first word that looks like a trading symbol)
    symbol_match = re.search(SYMBOL_PATTERN, text)
    if symbol_match:
        result['symbol'] = symbol_match.group(1).upper()
        result['confidence'] += 0.2
    
    # Extract direction (buy/sell)
    direction_match = re.search(DIRECTION_PATTERN, text, re.IGNORECASE)
    if direction_match:
        direction = direction_match.group(1).lower()
        # Normalize direction
        if direction in ['buy', 'long']:
            result['direction'] = 'buy'
        elif direction in ['sell', 'sel', 'short']:
            result['direction'] = 'sell'
        result['confidence'] += 0.2
    
    # Extract entry price
    # Look for patterns like "entry @1234" or "@ 1234" or "now @ 1234"
    entry_patterns = [
        r'(?:entry|@|at|now\s*@|limit\s*@?)\s*(\d+\.?\d*)',
        r'(?<=[^tp])@\s*(\d+\.?\d*)'  # @ symbol not preceded by "tp"
    ]
    
    for pattern in entry_patterns:
        entry_match = re.search(pattern, text, re.IGNORECASE)
        if entry_match:
            try:
                result['entry'] = float(entry_match.group(1))
                result['confidence'] += 0.2
                break
            except ValueError:
                pass
    
    # Extract take profit
    tp_match = re.search(r'(?:tp|take profit|target)(?!\s*2)\s*@?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if tp_match:
        try:
            result['tp1'] = float(tp_match.group(1))
            result['confidence'] += 0.1
        except ValueError:
            pass
    
    # Extract take profit 2
    tp2_match = re.search(r'(?:tp\s*2|tp2|take profit\s*2|target\s*2)\s*@?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if tp2_match:
        try:
            result['tp2'] = float(tp2_match.group(1))
            result['confidence'] += 0.1
        except ValueError:
            pass
    
    # Extract stop loss
    sl_match = re.search(r'(?:sl|stop loss|stop)\s*@?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if sl_match:
        try:
            result['sl'] = float(sl_match.group(1))
            result['confidence'] += 0.2
        except ValueError:
            pass
    
    return result

def test_parser(test_messages: List[str]) -> None:
    """
    Test the signal parser against a list of test messages.
    Prints the results for analysis.
    """
    for message in test_messages:
        print(f"\nTesting message: {message}")
        is_signal = is_trading_signal(message)
        print(f"Is trading signal: {is_signal}")
        
        if is_signal:
            parsed = parse_signal(message)
            print(f"Parsed result: {json.dumps(parsed, indent=2)}")

if __name__ == "__main__":
    # Test examples
    test_messages = [
        "#XAUUSD sell now @3257 tp @3247 tp2 @3232 Sl @3265",
        "XAUUSD SEL LIMIT @3237.5 tp @3229 Sl @3240",
        "XAUUSD sell now @ 3249 tp @ 3235 tp 2 @ 3202 SL @ 3257",
        "Just a regular message, not a trading signal",
        "Market update: EURUSD is looking bullish",  # Should not be detected as a signal
        "EURUSD BUY entry 1.0850 SL 1.0820 TP 1.0880",
        "#EURJPY SELL @ 158.240 SL 158.750 TP 157.500 TP2 156.750",
        "Entry 1.2345 Sl 1.2360 Tp 1.2420 GBPUSD Buy"  # Challenging format
    ]
    
    test_parser(test_messages)