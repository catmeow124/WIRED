# WIRED

**The WIRED Protocol**
Wide Interconnected Redistribution and Exchange of Data Network
> As of now, The current WIRED implementation supports (GET, COPY)

---

## GET

Retrieve a resource.

### Request

```text
GET
LOCATION: WIRED://SERVER1/GLOBAL/INDEX.TXT
.
```

### Response

```text
200 OK
LOCATION: WIRED://SERVER1/GLOBAL/INDEX.TXT
SIZE: 1234
TYPE: text/plain
.
[file bytes]
```

---

## POST

Create a resource.

### Request

```text
POST
TITLE: HELLO WORLD
DESCRIPTION: HELLO WORLD TEXT FILE
DESTINATION: WIRED://SERVER1/GLOBAL/HELLO.TXT
SIZE: 13
TYPE: text/plain
.
Hello, WIRED!
```

### Response

```text
201 CREATED
DESTINATION: WIRED://SERVER1/GLOBAL/HELLO.TXT
SIZE: 13
.
```

---

## COPY

Copy an existing resource, potentially between different WIRED servers.

### Request

```text
COPY
TITLE: HELLO WORLD
DESCRIPTION: HELLO WORLD TEXT FILE
SOURCE: WIRED://SERVER2/GLOBAL/HELLO.TXT
DESTINATION: WIRED://SERVER1/GLOBAL/HELLO.TXT
.
```

### Response

```text
201 CREATED
SOURCE: WIRED://SERVER2/GLOBAL/MYSITE2/HELLO.TXT
DESTINATION: WIRED://SERVER1/GLOBAL/MYSITE/HELLO.TXT
SIZE: 13
MESSAGE: File copied good
.
```

---

## EXCHANGE

Offer one resource in exchange for another. Servers accept or decline.

### Request

```text
EXCHANGE
REQUEST: WIRED://SERVER5/GLOBAL/INFO.TXT
OFFER: WIRED://SERVER3/GLOBAL/DOCUMENT.TXT
EXPIRE: 5000
.
```

### Response

```text
202 EXCHANGE CREATED
REQUEST: WIRED://SERVER5/GLOBAL/IDK/INFO.TXT
OFFER: WIRED://SERVER3/GLOBAL/COOLSTUFF/DOCUMENT.TXT
EXPIRE: 5000
.
```

---

## Methods


 `GET`       Retrieve a resource.                                                    
 `POST`      Create a resource.                                                      
 `COPY`      Copy an existing resource, potentially between different WIRED servers. 
 `EXCHANGE`  Offer one resource in exchange for another. Servers accept or decline.  
