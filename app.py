from flask import Flask, request,render_template
import collections
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize',methods=['POST'])
def summarize():
    def format_curr(num):
        if num<0:
            return f"-${abs(num)}"
        else:
            return f"${num}"
    
    json_string= request.form['Input']
    data = json.loads(json_string)
    avail_credit = data["creditLimit"]
    payable_balance = 0
    pending = collections.OrderedDict()   #maps pending txnIDs to list containing [amount, event_time]. Also maintains order in which keys were inserted.
    settled = collections.OrderedDict()   #maps settled txnIDs to list [amount, event_time, pending_event_time]. Also maintains order in which keys were inserted.
    
    for event in data["events"]:
        event_type = event["eventType"]
        if event_type == "TXN_AUTHED":
            pending[event["txnId"]] = [event["amount"], event["eventTime"]]
            avail_credit -= event["amount"]
        elif event_type == "TXN_SETTLED":
            settled[event["txnId"]] = [event["amount"], event["eventTime"], pending[event["txnId"]][1]]
            avail_credit = avail_credit + pending[event["txnId"]][0] - event["amount"] #add pending amount and subtract settled amount
            payable_balance += event["amount"]
            del pending[event["txnId"]]
        elif event_type == "TXN_AUTH_CLEARED":
            avail_credit += pending[event["txnId"]][0]
            del pending[event["txnId"]] #throws an error if no such txnid pending
        elif event_type == "PAYMENT_INITIATED":
            pending[event["txnId"]] = [event["amount"], event["eventTime"]]
            payable_balance += event["amount"]
        elif event_type == "PAYMENT_POSTED":
            settled[event["txnId"]] = [pending[event["txnId"]][0], event["eventTime"], pending[event["txnId"]][1]]
            avail_credit -= pending[event["txnId"]][0]
            del pending[event["txnId"]]
        elif event_type == "PAYMENT_CANCELED":
            payable_balance -= pending[event["txnId"]][0]
            del pending[event["txnId"]]
            
    res = "Available credit: " + str(format_curr(avail_credit)) + "\n" + "Payable balance: $" + str(payable_balance) + "\n" + "\n" + "Pending transactions: " + "\n"
    
    for pending_id in list(pending.keys())[::-1]:
        item = pending[pending_id]
        res += str(pending_id) + ": " + str(format_curr(item[0])) + " @ time " + str(item[1]) + "\n"
    
    res += "\n" +"Settled transactions: "
     
    for settled_id in list(settled.keys())[::-1][:3]: #prints only most recent three
        item = settled[settled_id]
        res += "\n" + str(settled_id) + ": " + str(format_curr(item[0])) + " @ time " + str(item[2]) + " (finalized @ time " + str(item[1]) + ")"

    res = res.replace('\n', '<br>')
    print(res)
    return render_template('index.html', available_credit=format_curr(avail_credit), payable_balance=format_curr(payable_balance), pending_transactions=pending, settled_transactions=settled)

if __name__ == "__main__":
    app.run(debug=True)