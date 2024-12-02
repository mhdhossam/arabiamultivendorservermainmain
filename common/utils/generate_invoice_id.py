import uuid


def generate_invoice_id():
    id = "MEDEX-INV-" + str(uuid.uuid4()).split("-")[1]

    return id
