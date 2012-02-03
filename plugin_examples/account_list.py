# This is a very simple plugin which simply lists all accounts in our document along with its type.
# It shows the basic read-only table plugin mechanisms.

# Import base class for our plugin
from core.plugin import ReadOnlyTablePlugin, Column
# Import utility functions and constant to manipulate account instances
from core.model.account import AccountType, sort_accounts

class AccountListPlugin(ReadOnlyTablePlugin):
    # The name that shows up when moneyGuru needs to list plugins
    NAME = 'Account List'
    
    # The columns that will be present in our table. For each column we add here, we have to set
    # a field value in each row we'll add in fill_table().
    COLUMNS = [
        Column('name', "Account Name"),
        Column('type', "Account Type"),
    ]
    
    # This is where the central part of the work is done. We fetch the accounts from the document
    # and we add a row to our table for each of these accounts.
    def fill_table(self):
        # accounts in the document are located in the 'accounts' attribute, and this attribute
        # behaves like a list so we can iterate over it.
        accounts = list(self.document.accounts)
        # We want to sort our accounts by type (asset, liability, income, expense) and then by name.
        # moneyGuru does it in a couple of other places, so there's a utility to do that,
        # sort_accounts(). We'll use that.
        sort_accounts(accounts)
        # Now let's add a row for each of our accounts.
        for account in accounts:
            # To add a row in a ReadOnlyTablePlugin, we have to call self.add_row() which returns
            # a row instance.
            row = self.add_row()
            # Now we need to fill our row's fields. The name is rather easy.
            row.set_field('name', account.name)
            # Now, the type is special. account.type is a constant that isn't "print-friendly" so
            # we need to set a name for each account type.
            account_type_display = {
                AccountType.Asset: "Asset",
                AccountType.Liability: "Liability",
                AccountType.Income: "Income",
                AccountType.Expense: "Expense",
            }[account.type]
            row.set_field('type', account_type_display)
    