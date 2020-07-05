# QR Code WiFi Scheme Regexs of Extreme Awesomeness

A few regular expressions to parse WIFI schemes such as:

    WIFI:T:WEP;S:test;P:rainbows\;unicorns\:jedis\,ninjas\\ secure;;

TLDR:

```python
ssid_re = r"(?P<ssid>(?<=S:)((?:[^\;\?\"\$\[\\\]\+])|(?:\\[\\;,:]))+(?<!\\;)(?=;))"
security_re = r"(?P<security>(?<=T:)[a-zA-Z]+(?=;))"
password_re = r"(?P<password>(?<=P:)((?:[;,:])|(?:[^;]))+(?<!;)(?=;))"
```

```python
all_re = r"(?P<ssid>(?<=S:)((?:[^\;\?\"\$\[\\\]\+])|(?:\\[\\;,:]))+(?<!\\;)(?=;))|(?P<security>(?<=T:)[a-zA-Z]+(?=;))|(?P<password>(?<=P:)((?:[;,:])|(?:[^;]))+(?<!;)(?=;))"
```

## Network Type

_Raw_

```regex
(?<=T:)[a-zA-Z]+(?=;)
```

_expanded_

```regex
    (?<=T:)       #Match the prefix T: but exclude from capture
        [a-zA-Z]+ #Any alpha character, 1 or more repetitions
    (?=;)         #Match the suffix ; but exclude from capture
```

## SSID

### Characters that are not allowed

    `? " $ \ [ ] +`

### Characters that must be escaped

    `\ ; , :`

_Raw_

```regex
(?<=S:)((?:[^\;\?\"\$\[\\\]\+])|(?:\\[\\;,:]))+(?<!\\;)(?=;)
```

_Java_

```regex
(?<=S:)((?:[^\\;\\?\\\"\\\$\\[\\\\\\]\\+])|(?:\\\\[\\\\;,:]))+(?<!\\\\;)(?=;)
```

_expanded_

```
    (?<=S:)                         #Match the prefix S: but exclude from capture
        (                           #Choose from the following 2 choices
            (?:[^\;\?\"\$\[\\\]\+]) #Anything that isn't one of the restricted characters
            |                       #OR
            (?:\\[\\;,:])           #An escaped special character
        )+                          #1 or more repititions
    (?<!\\;)(?=;)                   #Match a ; only if there isn't a \; before it
```

## Password

_Raw_

```regex
(?<=P:)((?:[;,:])|(?:[^;]))+(?<!;)(?=;)

```

_Java_

```
(?<=P:)((?:[;,:])|(?:[^;]))+(?<!;)(?=;)

```

_expanded_

```regex
    (?<=P:)                 #Match the prefix S: but exclude from capture
        (                   #Choose from the following 2 choices
            (?:\\[\\;,:])   #An escaped special character
            |               #OR
            (?:[^;])        #Any character that isn't a ;
        )+                  #1 or more repititions
    (?<!\\;)(?=;)           #Match a ; only if there isn't a \; before it
```
