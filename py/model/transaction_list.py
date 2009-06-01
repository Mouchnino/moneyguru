# Unit Name: moneyguru.model.transaction_list
# Created By: Virgil Dupras
# Created On: 2008-09-14
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

class TransactionList(list):
    def add(self, transaction, keep_position=False, position=None):
        """Adds 'transaction' to self
        
        If you want transaction.position to stay intact, call with keep_position at True. If you 
        specify a position, this is the one that will be used.
        """
        if position is not None:
            transaction.position = position
        elif not keep_position:
            transactions = self.transactions_at_date(transaction.date)
            if transactions:
                transaction.position = max(t.position for t in transactions) + 1
        self.append(transaction)
    
    def clear(self):
        del self[:]
    
    def reassign_account(self, account, reassign_to=None):
        """Removes 'account' reference in all transactions"""
        for transaction in self[:]:
            transaction.reassign_account(account, reassign_to)
            if not transaction.affected_accounts():
                self.remove(transaction)
    
    def move_before(self, from_transaction, to_transaction):
        """Moves from_transaction just before to_transaction
        
        If to_transaction is None, from_transaction is moved to the end of the
        list. You must recook after having done a move (or a bunch of moves)
        """
        if from_transaction not in self:
            return
        if to_transaction is not None and to_transaction.date != from_transaction.date:
            to_transaction = None
        transactions = self.transactions_at_date(from_transaction.date)
        transactions.remove(from_transaction)
        if not transactions:
            return
        if to_transaction is None:
            target_position = max(t.position for t in transactions) + 1
        else:
            target_position = to_transaction.position
        from_transaction.position = target_position
        for transaction in transactions:
            if transaction.position >= target_position:
                transaction.position += 1
    
    def move_last(self, transaction):
        self.move_before(transaction, None)
    
    def transactions_at_date(self, target_date):
        return set(t for t in self if t.date == target_date)
    
