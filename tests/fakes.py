

class FakePictureRepository:
    def __init__(self, pictures=None):
        self.pictures = pictures or []

    def get_by_id_and_user(self, id, user_id):
        for p in self.pictures:
            if p.id == id and p.user_id == user_id and p.deleted_at is None:
                return p
        return None

    def add(self, picture):
        self.pictures.append(picture)
        return picture

    def get_by_id(self, id):
        for p in self.pictures:
            if p.id ==id and p.deleted_at is None:
                return p
        return None

    def list_by_user(self, user_id, limit, offset):
        result = []
        for p in self.pictures:
            if p.user_id == user_id and p.deleted_at is None:
                result.append(p)
        return result[offset: offset + limit]

    def count_by_user(self, user_id):
        result = 0
        for p in self.pictures:
            if p.user_id == user_id and p.deleted_at is None:
                result += 1
        return result


class FakeUserRepository:

    def __init__(self, users=None):
        self.users = users or []

    def get_by_email(self, email):
        for u in self.users:
            if u.email == email:
                return u
        return None

    def add_user(self, user):
        self.users.append(user)

    def get_by_id(self, id):
        for u in self.users:
            if u.id == id:
                return u
        return None

    def increment_token_version(self, user):
        for u in self.users:
            if u.id == user.id:
                u.token_version += 1


class FakeStorageClient:
    def __init__(self):
        self.objects = {}

    def upload(self, key, data, content_type):
        self.objects[key] = data

    def generate_presigned_url(self, key):
        return f"https://fake-storage/{key}"

    def download(self, key):
        return self.objects[key]

    def delete(self, key):
        self.objects.pop(key, None)
                