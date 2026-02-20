def longestSubstring(s: str) -> int:
    '''输出无重复字母的最长子串长度'''
    left = 0
    right = 0
    max_length = 0
    window = set()
    while right < len(s):
        if s[right] not in s[left:right]:
            window.add(s[right])
            right += 1
            max_length = max(max_length, right - left)
        else:
            window.remove(s[left])
            left += 1
    return max_length


def longestSubstring2(s: str) -> list[str]:
    '''输出无重复字母的最长子串,将这些最长子串返回一个列表'''
    left = 0
    right = 0
    max_length = 0
    result: set[str] = set()
    while right < len(s):
        if s[right] not in s[left:right]:
            right += 1
            length = right - left
            if length > max_length:
                max_length = length
                result = {s[left:right]}
            elif length == max_length:
                result.add(s[left:right])
        else:
            left += 1
    return list(result)

if __name__ == "__main__":
    print(longestSubstring("abcabcbb"))   # 3
    print(longestSubstring2("abcabcbb"))  # ['abc', 'bca', 'cab']
    
