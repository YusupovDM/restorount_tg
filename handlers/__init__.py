from handlers import booking, inline, payment, start

# Порядок важен: команды (/start, /cancel, /mybookings) должны срабатывать
# раньше, чем «ловушки» неверного ввода внутри FSM в booking.router
routers = [start.router, payment.router, inline.router, booking.router]
