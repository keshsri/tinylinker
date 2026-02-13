from typing import Dict

def parse_user_agent(user_agent: str) -> Dict[str, str]:
    ua_lower = user_agent.lower()
    device = detect_device(ua_lower)
    browser = detect_browser(ua_lower)
    os = detect_os(ua_lower)

    return {
        'device': device,
        'browser': browser,
        'os': os
    }

def detect_device(ua: str) -> str:
    if any(keyword in ua for keyword in ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']):
        return 'mobile'
    elif any(keyword in ua for keyword in ['ipad', 'tablet']):
        return 'tablet'
    elif any(keyword in ua for keyword in ['windows', 'macintosh', 'linux', 'x11']):
        return 'desktop'
    return 'unknown'

def detect_browser(ua: str) -> str:
    if 'edg' in ua:
        return 'Edge'
    elif 'chrome' in ua and 'edg' not in ua:
        return 'Chrome'
    elif 'firefox' in ua:
        return 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        return 'Safari'
    elif 'opera' in ua or 'opr' in ua:
        return 'Opera'
    return 'Unknown'

def detect_os(ua: str) -> str:
    if 'windows' in ua:
        return 'Windows'
    elif 'mac os' in ua or 'macos' in ua:
        return 'macOS'
    elif 'linux' in ua and 'android' not in ua:
        return 'Linux'
    elif 'android' in ua:
        return 'Android'
    elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
        return 'iOS'
    return 'Unknown'