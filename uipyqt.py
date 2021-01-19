import sys
from PyQt5.QtWidgets import *
import tactics

class ScopaForm(QDialog):

    opponent_buttons = []
    table_buttons = []
    my_hand_buttons = []

    last_claimed_hand = 0

    def __init__(self, sc, parent=None):
        super(ScopaForm, self).__init__(parent)
        self.sc = sc

        # draw the form with three horizontal layouts on top of each other
        self.main_layout=QVBoxLayout()
        self.main_layout.addWidget(QLabel(tactics.opponent_hand_frame_name))
        self.opponent_hand_layout=QHBoxLayout()

        self.main_layout.addLayout(self.opponent_hand_layout)

        #draw table
        self.group_box = QGroupBox(tactics.table_frame_name)
        self.vbox = QHBoxLayout()

        self.group_box.setLayout(self.vbox)
        self.main_layout.addWidget(self.group_box)

        # draw my hand
        self.main_layout.addWidget(QLabel(tactics.my_hand_frame_name))
        self.my_hand_layout=QHBoxLayout()


        self.main_layout.addLayout(self.my_hand_layout)

        # add action buttons
        self.main_layout.addWidget(QLabel(tactics.actions_frame_name))

        self.my_action_layout=QHBoxLayout()

        # then add two buttons - for claiming the cards from the table
        self.claim_cards_button = QPushButton(tactics.claim_cards_button_name)
        self.claim_cards_button.clicked.connect(self.pressed_claim_cards)
        self.my_action_layout.addWidget(self.claim_cards_button)
        # ...and for laying the card on the table
        self.lay_card_button = QPushButton(tactics.lay_card_button_name)
        self.lay_card_button.clicked.connect(self.pressed_lay_card)
        self.my_action_layout.addWidget(self.lay_card_button)
        # and OK button
        self.OK_button = QPushButton("OK")
        self.OK_button.clicked.connect(self.pressed_OK)
        self.my_action_layout.addWidget(self.OK_button)

        self.main_layout.addLayout(self.my_action_layout)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Scopa")

    # removes all widgets from given layout
    def remove_all_widgets(self, layout):
        widget_range=reversed(range(layout.count()))
        for i in widget_range:
            widgetToRemove = layout.itemAt(i).widget()
            button_name = widgetToRemove.text()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    # this function clears the form from all items in the view
    # empties all the global collections
    # and sets all the flags to False
    def clear_form(self):
        self.remove_all_widgets(self.opponent_hand_layout)
        self.opponent_buttons=[]

        self.remove_all_widgets(self.vbox)
        self.table_buttons=[]

        self.remove_all_widgets(self.my_hand_layout)
        self.my_hand_buttons=[]

    # sets buttons "Claim cards" and "Lay card" as visible, OK as invisible
    def enable_button_for_my_move(self):
        self.claim_cards_button.setVisible(True)
        self.lay_card_button.setVisible(True)
        self.OK_button.setVisible(False)

    # sets button OK as visible, "Claim cards" and "Lay card" as invisible
    def enable_button_for_opponent_move(self):
        self.claim_cards_button.setVisible(False)
        self.lay_card_button.setVisible(False)
        self.OK_button.setVisible(True)

    # draw opponent hand making only the button indicated enabled and checked
    def draw_opponent_hand(self, card_to_display = ""):
        if card_to_display!="":
            displayed_button = QPushButton(card_to_display)
            displayed_button.setEnabled(True)
            displayed_button.setCheckable(True)
            displayed_button.setChecked(True)
            self.opponent_hand_layout.addWidget(displayed_button)
            self.opponent_buttons.append(displayed_button)

        for opponent_card in self.sc.hands[1]:
            opponent_button = QPushButton("XX")
            opponent_button.setEnabled(False)
            # add button for each opponent hand
            self.opponent_hand_layout.addWidget(opponent_button)
            self.opponent_buttons.append(opponent_button)

    def draw_table(self, disable_cards_not_displayed, cards_to_display=[]):

        # show button for each card on the table
        for table_card in self.sc.table:
            table_button = QPushButton(table_card)
            table_button.setGeometry(200, 150, 100, 40)
            table_button.setCheckable(True)
            if disable_cards_not_displayed:
                table_button.setEnabled(False)
            table_button.clicked.connect(self.enable_actions)
            self.vbox.addWidget(table_button)
            self.table_buttons.append(table_button)

        for displayed_card in cards_to_display:
            if displayed_card != cards_to_display:
                displayed_button = QPushButton(displayed_card)
                displayed_button.setGeometry(200, 150, 100, 40)
                displayed_button.setEnabled(True)
                displayed_button.setCheckable(True)
                displayed_button.setChecked(True)
                self.vbox.addWidget(displayed_button)
                self.table_buttons.append(displayed_button)

    def draw_my_hand(self, show_as_active):
        # show button for each card in hand
        for my_card in self.sc.hands[0]:
            my_button = QPushButton(my_card)
            my_button.setEnabled(show_as_active)
            my_button.setCheckable(show_as_active)
            # make sure all the other are unchecked
            my_button.clicked.connect(self.disable_all_but_this)
            self.my_hand_layout.addWidget(my_button)
            self.my_hand_buttons.append(my_button)

    # this method prepares the form for my move
    def my_move(self):
        self.sc.draw_hand_if_necessary(0)
        my_hand=self.sc.hands[0]
        self.clear_form()

        self.draw_opponent_hand()
        self.draw_table(False)
        self.draw_my_hand(True)

        self.enable_button_for_my_move()
        self.enable_actions()

    # display the form for opponent move
    def opponent_move(self):
        take=self.sc.play_hand(1)
        card_from_hand=take[0]
        cards_from_table=take[1]

        self.clear_form()

        self.draw_opponent_hand(card_from_hand)
        self.draw_table(True, cards_from_table)
        self.draw_my_hand(False)

        if len(cards_from_table)>0:
            self.last_claimed_hand = 1

        self.enable_button_for_opponent_move()


        #draw both hands if are empty
        self.sc.draw_hand_if_necessary(0)
        no_more_cards = self.sc.draw_hand_if_necessary(1)
        if no_more_cards:
            self.finish_game()


    # uncheck any buttons other than the one clicked
    def disable_all_but_this(self):
        for btn in self.my_hand_buttons:
            if not btn is self.sender():
                btn.setChecked(False)

        self.enable_actions()

    # enable actions: the sum of checked button cards on the table must be equal to
    # checked card from hand for claiming cards.
    # No cards on the table and one hand card can be checked for laying card in hand
    def enable_actions(self):
        table = []
        table_card_set = False
        for table_btn in self.table_buttons:
            if table_btn.isChecked():
                table.append(table_btn.text())
                table_card_set=True

        sum_of_table=tactics.sum_of_cards(table)

        hand_card_set=False
        hand_card_value=-1
        for hand_btn in self.my_hand_buttons:
            if hand_btn.isChecked():
                hand_card_set=True
                hand_card_value=int(hand_btn.text()[:2])

        self.lay_card_button.setEnabled(hand_card_set and not table_card_set)

        self.claim_cards_button.setEnabled(hand_card_set and sum_of_table == hand_card_value)

    # again human move
    def pressed_OK(self):
        self.my_move()

    # remove card from hand and add it to the table
    def pressed_lay_card(self):
        for button in self.my_hand_buttons:
            if button.isChecked():
                laid_card = button.text()
                self.sc.hands[0].remove(laid_card)
                self.sc.table.append(laid_card)
                break

        # now it's computer's move
        self.opponent_move()

    # remove card from hand, cards from the table - and add them to pile
    def pressed_claim_cards(self):
        for button2 in self.my_hand_buttons:
            if button2.isChecked():
                card_from_hand=button2.text()
                self.sc.hands[0].remove(card_from_hand)
                self.sc.piles[0].append(card_from_hand)
                break

        for button in self.table_buttons:
            if button.isChecked():
                card_from_table=button.text()
                self.sc.table.remove(card_from_table)
                self.sc.piles[0].append(card_from_table)

        # if table is empty, calculate scopa
        if len(self.sc.table) == 0:
            self.sc.scopa_count[0] += 1
            qmsg = QMessageBox()
            qmsg.setWindowTitle("Scopa")
            qmsg.setText(tactics.this_was_scopa)
            qmsg.exec_()

        self.last_claimed_hand = 0
        self.opponent_move()

    # if no cards in game claim remaining cards for the player who made the last claim
    def finish_game(self):
        for card in self.sc.table.copy():
            self.sc.piles[self.last_claimed_hand].append(card)
            self.sc.table.remove(card)

        my_score = self.sc.calculate_score(0)
        opponent_score = self.sc.calculate_score(1)

        message = "Moje karty: " + str(len(self.sc.piles[0])) + ", w tym denarów "
        message += str(tactics.denars(self.sc.piles[0])) + ", wynik: " + str(my_score)
        message += "\nPrzeciwnika: " + str(len(self.sc.piles[1])) + ", w tym denarów "
        message += str(tactics.denars(self.sc.piles[1])) + " wynik: " + str(opponent_score)


        msg = QMessageBox()
        msg.setText("Scopa finished")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        # self.sc.print_game_results()
        sys.exit(0)






