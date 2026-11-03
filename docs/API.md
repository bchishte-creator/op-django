# Food tracker REST API

The API is rooted at `/api/`. It uses Django REST Framework viewsets and the same database models as the HTML pages. It supports the standard list, detail, create, replace, partial-update, and delete operations. For this training project, endpoints are unauthenticated as permitted in Part 3; run them only in a local or otherwise trusted environment.

## Endpoints

| Resource | Collection | Detail |
|---|---|---|
| Categories | `/api/categories/` | `/api/categories/{id}/` |
| People | `/api/people/` | `/api/people/{id}/` |
| Foods | `/api/foods/` | `/api/foods/{id}/` |
| Food events | `/api/events/` | `/api/events/{id}/` |

Collection endpoints support `GET` and `POST`. Detail endpoints support `GET`, `PUT`, `PATCH`, and `DELETE`. Collection responses are paginated; use `?page=2` to request another page.

## Food event fields

`food`, `consumer`, and `category` are IDs returned by their respective collection endpoints. Related display names are included as read-only fields.

```json
{
  "food": 1,
  "consumer": 1,
  "category": 1,
  "consumed_at": "2026-11-02T12:30:00Z",
  "notes": "Team lunch"
}
```

Send this JSON to `POST /api/events/`. For a photo, send the same fields as `multipart/form-data` and include the uploaded image under `photo` (maximum 5 MB).

## Search and filtering

- `GET /api/events/?search=yogurt` searches food name, person, category, and notes.
- `GET /api/events/?category=2&consumer=1&food=3` filters by related record IDs.
- `GET /api/events/?from_date=2026-11-01&to_date=2026-11-02` filters by an inclusive date range.
- `GET /api/events/?ordering=consumed_at` sorts oldest first; prefix with `-` for newest first.
