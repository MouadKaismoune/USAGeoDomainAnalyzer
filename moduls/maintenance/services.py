from database import db


def get_unknown_domains():
    return db.fetch_all(
        "SELECT * FROM domains WHERE status NOT LIKE '%Available%' AND status NOT LIKE '%Registered%' ORDER BY city, niche"
    )


def update_domain_status(domain_id, new_status):
    db.execute(
        "UPDATE domains SET status = ? WHERE id = ?",
        (new_status, domain_id),
    )


def delete_unknown_domains():
    db.execute(
        "DELETE FROM domains WHERE status NOT LIKE '%Available%' AND status NOT LIKE '%Registered%'"
    )
