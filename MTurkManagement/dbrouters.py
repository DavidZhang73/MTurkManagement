class DBRouter:

    def db_for_read(self, model, **hints):
        if not hasattr(model, 'Param'):
            return None
        return getattr(model.Param, 'db', None)

    def db_for_write(self, model, **hints):
        if not hasattr(model, 'Param'):
            return None
        return getattr(model.Param, 'db', None)
