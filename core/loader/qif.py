# Created By: Virgil Dupras
# Created On: 2008-02-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import re
from collections import namedtuple

from hscommon.util import first, stripfalse

from ..exception import FileFormatError
from ..model.account import AccountType
from . import base

# LITTLE NOTE ON QIF AND SPLITS
# The splits in QIF work in an awkward way which needs to be described here.
# First of all, the Total amount for the context account is always defined in the T field. This is
# the amount that has to go in that split. Then come the splits. However, the splits amounts are
# ***REVERSED***. Yes, ***REVERSED***. If, for example, I have a split between A B and C. A is
# debited for 3, B is credited for 4 and C is debited for 1. The end result will be:
# T3
# SB
# $4
# SC
# $-1

# ABOUT AutoSwitch
# This option is some kind of way to make a QIF file have extra info about accounts for which there
# are no txns. We ignore those. However, some QIF exporter have the good idea to not correctly clear
# the option flag, so this is a mess. What we do here is that we ignore the flag and always keep the
# last acount in a row of multiple account where there is not txns in between

# anything that is not part of an amount
re_not_amount = re.compile(r'[^\d.,\-]+')

ENTRY_HEADERS = {'Type:Bank', 'Type:Invst', 'Type:Cash', 'Type:Oth A', 'Type:CCard', 'Type:Oth L'}

class BlockType:
    Account = 1
    Entry = 2
    Other = 3

Line = namedtuple('Line', 'header data')

class Block:
    def __init__(self):
        self.type = BlockType.Other
        self.lines = []
    
    def get_line(self, line_header):
        return first(line for line in self.lines if line.header == line_header)
    

class Loader(base.Loader):
    def _parse(self, infile):
        content = infile.read()
        lines = stripfalse(content.split('\n'))
        blocks = []
        autoswitch_blocks = [] # blocks in the middle of an AutoSwitch option
        block = Block()
        current_block_type = BlockType.Entry
        autoswitch_mode = False
        for line in lines:
            header, data = line[0], line[1:].strip()
            if header == '!':
                if data == 'Account':
                    current_block_type = BlockType.Account
                elif data in ENTRY_HEADERS:
                    current_block_type = BlockType.Entry
                    if autoswitch_mode:
                        # We have a buggy qif that doesn't clear its autoswitch flag. The last block
                        # we added to autoswitch actually belonged to normal blocks. move it.
                        if autoswitch_blocks:
                            blocks.append(autoswitch_blocks.pop())
                        autoswitch_mode = False
                elif data.startswith('Type:'): # if it doesn't, just ignore it
                    current_block_type = BlockType.Other
                elif data == 'Option:AutoSwitch':
                    autoswitch_mode = True
                elif data == 'Clear:AutoSwitch':
                    autoswitch_mode = False
            elif header == '^':
                if current_block_type != BlockType.Other:
                    block.type = current_block_type
                    if block.type == BlockType.Entry:
                        # Make sure we have a valid entry block (which has a valid date) and change
                        # the type if it's not the case.
                        date_line = block.get_line('D')
                        if date_line is None or self.clean_date(date_line.data) is None:
                            block.type = BlockType.Other
                    if autoswitch_mode:
                        autoswitch_blocks.append(block)
                    else:
                        blocks.append(block)
                block = Block()
                if current_block_type == BlockType.Account and not autoswitch_mode:
                    current_block_type = BlockType.Entry
            if header != '^':
                block.lines.append(Line(header, data))
        if not blocks:
            raise FileFormatError()
        logging.debug('This is a QIF file. {0} blocks'.format(len(blocks)))
        entry_blocks = [block for block in blocks if block.type == BlockType.Entry]
        date_lines = (block.get_line('D') for block in entry_blocks)
        str_dates = [line.data for line in date_lines if line]
        self.date_format = self.guess_date_format(str_dates)
        if self.date_format is None:
            raise FileFormatError()
        self.blocks = blocks
        self.autoswitch_blocks = autoswitch_blocks
    
    def _load(self):
        seen_account_names = set()
        
        def remove_brackets(name):
            if name.startswith('[') and name.endswith(']'):
                return name[1:-1].strip()
            else:
                return name
        
        def parse_account_line(header, data):
            if header == 'N':
                self.account_info.name = data.strip()
            if header == 'T' and data in ('Oth L', 'CCard'):
                self.account_info.type = AccountType.Liability
        
        def parse_split_line(header, data):
            if header == 'S':
                data = remove_brackets(data)
                if data != self.account_info.name and data in seen_account_names:
                    # This transaction has already been added from the other account(s)
                    self.cancel_transaction()
                self.split_info.account = data
            elif header == 'E':
                self.split_info.memo = data
            elif header == '$':
                self.split_info.amount = re_not_amount.sub('', data)
                self.split_info.amount_reversed = True # Split amounts in QIF are REVERSED
        
        def parse_entry_line(header, data):
            if header == 'D':
                try:
                    self.transaction_info.date = self.parse_date_str(data, self.date_format)
                except ValueError:
                    pass
            elif header == 'M':
                self.transaction_info.description = data
            elif header == 'P':
                self.transaction_info.payee = data
            elif header == 'N':
                self.transaction_info.checkno = data
            elif header == 'L':
                data = remove_brackets(data)
                if data in seen_account_names:
                    # This transaction has already been added from the other account(s)
                    self.cancel_transaction()
                else:
                    self.transaction_info.transfer = data
            elif header == 'T':
                self.transaction_info.amount = re_not_amount.sub('', data)
            elif header == '!': # yeah, this thing is in the entry data...
                if data in ('Type:CCard', 'Type:Oth L'):
                    self.account_info.type = AccountType.Liability
        
        # Send "empty" accounts to the autoswitch_blocks list
        for block, nextblock in zip(self.blocks[:], self.blocks[1:]+[None]):
            if block.type == BlockType.Account and (nextblock is None or nextblock.type != BlockType.Entry):
                self.autoswitch_blocks.append(block)
                self.blocks.remove(block)
        for block in self.blocks:
            block_type = block.type
            lines = block.lines
            if block_type == BlockType.Account:
                self.start_account()
                for header, data in lines:
                    parse_account_line(header, data)
                if self.account_info.name:
                    seen_account_names.add(self.account_info.name)
            elif block_type == BlockType.Entry:
                if not seen_account_names:
                    self.account_info.name = 'Account' # If no account has been seen yet, add the txn to a defult 'Account' one
                seen_split_fields = set()
                for header, data in lines:
                    if header in ('S', 'E', '$'): # splits field
                        if header in seen_split_fields: #must flush the split
                            self.flush_split()
                            seen_split_fields.clear()
                        parse_split_line(header, data)
                        seen_split_fields.add(header)
                        continue
                    parse_entry_line(header, data)
                self.flush_transaction()
        self.flush_account()
        # For accounts that haven't been added in normal blocks, we complete the list with autoswitch
        # blocks (so that we can have correct types for income/expense accounts)
        for block in self.autoswitch_blocks:
            block_type = block.type
            lines = block.lines
            if block_type == BlockType.Account:
                self.start_account()
                for header, data in lines:
                    parse_account_line(header, data)
                if self.account_info.name in seen_account_names:
                    self.cancel_account()
                else:
                    seen_account_names.add(self.account_info.name)
                    self.flush_account()
    
