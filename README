# csp-ip-lookup

## Quick Usage

Go to the following website and punch in the IP Address

https://catscrdl.retool.com/apps/d6f55d20-8560-11ec-b98c-bb2f02c48831/CSP%20Finder

Or you can use a curl command to lookup multiple IP addresses

```
$ curl -X POST https://csp-ip-lookup.catscrdl.io/collectCSPsPublicAPI  --header 'Content-Type: application/json' -d '{
  "ip_addresses": [
    "52.127.53.105",
    "35.134.66.241",
    "99.87.32.45"
  ]
}'
```

## Caching

You can choose to set an optional flag in the JSON body called "cached". If you set this to "y", then the lookup will use a cached value of the CSP IP ranges. This cache updates about every 15 minutes. If this value is "n" or otherwise omitted, it'll use a live lookup. The live lookup may be more accurate but it will also take longer.