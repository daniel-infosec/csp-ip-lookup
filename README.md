# csp-ip-lookup

## Quick Usage

Go to the following website and punch in the IP Address

https://catscrdl.retool.com/embedded/public/e927ef61-2853-4b36-9993-47fa7e6011d3

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