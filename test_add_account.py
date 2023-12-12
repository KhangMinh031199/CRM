import api
from validate_email import validate_email

password = "@A123456@"
email = "hailh2@techcombank.com.vn"

recs = api.get_accounts_merchants("652acc252d4a4762b43d9d55")
print (recs)

def sign_in_by_account_email(merchant_id, email, password):
    user = api.DATABASE.accounts.find_one(
        {'merchant_id': merchant_id, 'email': email})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and api.check_hash(password, pass_hash):
        return user
    else:
        return False
    
is_email_merchant = validate_email(email)
print (is_email_merchant)
merchant_email = api.get_merchant_by_email(email)
print (merchant_email)
is_email = validate_email(email)
print (is_email)
user = sign_in_by_account_email("652acc252d4a4762b43d9d55", email, password )
role = user.get('roles')
print (role)
if role == '3':
    print("fukx")
else:
    print ("wtf")

merchant = api.get_merchant_by_slug("techcombank")
print (merchant)