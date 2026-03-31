# Data

Stack Exchange activity data, organized by community.

Each subdirectory corresponds to a Stack Exchange site where at least one question or answer has been posted. Directories are named using the site's API identifier (e.g., `stackoverflow`, `hermeneutics`, `cooking`).

## Structure

```
data/
├── stackoverflow/
│   ├── README.md      # Profile: reputation, badges, member since
│   ├── answers.md     # All answers, sorted by score (highest first)
│   └── questions.md   # All questions, sorted by score (highest first)
├── hermeneutics/
│   └── ...
└── ...
```

## Source

All data is fetched from the [Stack Exchange API v2.3](https://api.stackexchange.com/docs) using the `/users/{id}/answers` and `/users/{id}/questions` endpoints.
