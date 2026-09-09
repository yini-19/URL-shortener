# URL-shortener(urlshorts.com)
A service that takes a long URL and gives back a short one, and when someone visits the short one, they are redirected back to the original.

## Actors
1. Creator of the short URL
2. The user of the short URL

## Creation flow
User submits a long URL -> system generates a short code -> short code and long URL are stored as a pair -> short URL is returned to the user

## Redirect flow
User visits the shortened URL -> system looks up the url -> system finds the matching long url -> system redirects user to the original URL

## Success
For creation: short URL is successfully generated and returned to the user
For redirect: short URL successfully redirects user to the right original page

## Out of scope for version 1:

* User accounts / authentication (anyone can create a short link, no login required)
* Custom aliases (user choosing their own short code instead of a generated one)
* Click analytics / dashboards (tracking visits, referrers, geographic data)
* Link expiration or scheduled deletion
* Rate limiting on link creation
* Editing or deleting an existing short link
* A frontend UI (start with API endpoints only, no web page)
* QR code generation
* Bulk/batch URL shortening
* Custom domains

## Candidate approaches:
1. Random string generation
2. incrementing counter converted to base62
3. hashing the long URL (e.g., MD5/SHA and truncating)

## my approach and reason
Random string generation: this is simple but unpredictable. unpredictability is my priority in order to keep users urls safe. with random string generation, generated strings cant be predicted which makes it efficient for me. There is a possibility of having duplicate generated string. as a result there will be a seperate logic for duplicate check

## Code length and character set
code will be 6 character long. It will consist of letters and digits. 0 and O will be excluded as well as 1 and l in order to avoid ambiguity and confusion

## short url must remember
1. short code - text
2. original url - text
3. creation timestamp - date/time
4. click count - whole number (i want a click counter in order to note the success of this site)
5. email - text

## code | original_url | created_at | clicks

## Required vs optional:

* code — required, always present (this is how records get looked up)
* original_url — required, always present (no point in a record without it)
* created_at — required, but has a sensible default: automatically set to "now" when the record is created, so the user/system never has to supply it manually
* clicks — required, but defaults to 0 when a record is first created (it should never be missing or null, just start at zero and increment from there)

## Uniqueness rules:

* code must be unique — no two records can ever share the same short code, since that's literally what the redirect lookup depends on
* original_url does not need to be unique — the same long URL can have multiple different short codes pointing to it

## Choosing and setting up persistence layer

In-memory structure will be a dictionary; the code is the key, everything else (original_url, created_at, clicks) is the value.

The values themselves will be stored as dictionaries because it is faster to reaso about and easier to deal with for a start

in-memory storage resets every time the server restarts; this is fine for now because it lets me build and test the create/redirect logic before adding real persistence.

## actions the storage should support:

1. "save a new record," 
2. "look up a record by code," and 
3. "increment the click count for a code."


----------------------------------------
|Column    | SQL Type    | Constraints |
----------------------------------------
|code      | TEXT        |	PRIMARY KEY |
---------------------------------------
|original_url | TEXT     |	NOT NULL  |
---------------------------------------
creator_email |	TEXT |	NOT NULL (assuming every link must be tied to a creator — see note below)|
-------------------
created_at | TIMESTAMP |	NOT NULL DEFAULT CURRENT_TIMESTAMP|
-------------
clicks | INTEGER | NOT NULL DEFAULT 0|
-------



* I will implement the same three operations (save, look up, increment) using SQLite instead of a dictionary, so the rest of my code doesn't need to change.