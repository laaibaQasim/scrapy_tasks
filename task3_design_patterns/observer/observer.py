from abc import ABC, abstractmethod


class Observer(ABC):
	@abstractmethod
	def update(self, item):
		pass


class Producer(Observer):
	def __init__(self):
		self.quantity = 0

	def update(self, item):
		self.quantity = item.quantity
		print("Producer gets notified.")

		if self.quantity < 1:
			self.produce_item()

	def produce_item(self):
		pass


class Buyer(Observer):
	def __init__(self):
		self.available_quantity = 0

	def update(self, item):
		self.available_quantity = item.quantity
		print("Buyer gets notified.")


class Item:
	def __init__(self, quantity):
		self.quantity = quantity
		self.observers = []
	
	def set_quantity(self, quantity):
		self.quantity = quantity
		
	def buy(self):
		self.quantity -= 1
		self.notify()
		
	def subscribe(self, observer):
		self.observers.append(observer)
		
	def unsubscribe(self, observer):
		self.observers.remove(observer)
		
	def notify(self):
		for observer in self.observers:
			observer.update(self)
		

if __name__ == '__main__':
	item = Item(5)
	item.subscribe(Producer())
	item.subscribe(Buyer())

	item.buy()
	