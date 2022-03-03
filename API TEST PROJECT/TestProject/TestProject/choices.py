invoice_status = (
    ("pending","Pending"),
)

scheduler_status = (
   ("pending","Pending"),
   ("call_due","Call due"),
   ("call_done","Call done"),
   ("in_progress","In progress"),
   ("finished","Finished"),
   ("legal_action","Legal Action"),

)

action_types = (
    ("call","Call"),
    ("email","Email"),
    ("chat","Chat"),
    ("offline_message","Offline message"),
    # ("ticket","Ticket"),
    # ("plan_follow_up","Plan Follow up"),
)

action_status = (
    ("done","Processed"),
    ("due","Follow up"),
    ("finished","Finished"),
)
doc_type = (("general", "General"), ("invoice", "Invoice"), ("order", "Order"))
