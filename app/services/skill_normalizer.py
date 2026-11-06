SKILL_ALIASES = {

    "aws": "amazon web services",
    "amazon aws": "amazon web services",
    "amazon web services": "amazon web services",

    "postgres": "postgresql",
    "postgres db": "postgresql",
    "postgresql": "postgresql",

    "reactjs": "react",
    "react.js": "react",
    "react": "react",

    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",

    "ml": "machine learning",
    "machine learning": "machine learning",

    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",

    "genai": "generative ai",
    "gen ai": "generative ai",
    "generative ai": "generative ai",

    "k8s": "kubernetes",
    "kubernetes": "kubernetes",

    "py": "python",
    "python": "python",

    "js": "javascript",
    "javascript": "javascript",

    "ts": "typescript",
    "typescript": "typescript",

    "restful api": "rest api",
    "rest api": "rest api"
}


def normalize_skill(
    skill: str
) -> str:

    normalized = (
        skill
        .lower()
        .strip()
    )

    normalized = " ".join(
        normalized.split()
    )

    return SKILL_ALIASES.get(
        normalized,
        normalized
    )