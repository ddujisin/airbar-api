import type { MenuItem } from '@/types/api';

interface CartItem {
  itemId: string;
  name: string;
  price: number;
  quantity: number;
}

interface Cart {
  items: CartItem[];
  reservationId?: string;
  pin?: string;
}

const CART_KEY = 'airbar_cart';

export const getCart = (): Cart => {
  const cartData = sessionStorage.getItem(CART_KEY);
  return cartData ? JSON.parse(cartData) : { items: [] };
};

export const addToCart = (item: CartItem) => {
  const cart = getCart();
  const existingItem = cart.items.find(i => i.itemId === item.itemId);

  if (existingItem) {
    existingItem.quantity += item.quantity;
  } else {
    cart.items.push(item);
  }

  sessionStorage.setItem(CART_KEY, JSON.stringify(cart));
};

export const updateQuantity = (itemId: string, quantity: number) => {
  const cart = getCart();
  cart.items = cart.items
    .map(item => item.itemId === itemId ? { ...item, quantity } : item)
    .filter(item => item.quantity > 0);

  sessionStorage.setItem(CART_KEY, JSON.stringify(cart));
};

export const removeFromCart = (itemId: string) => {
  const cart = getCart();
  cart.items = cart.items.filter(item => item.itemId !== itemId);
  sessionStorage.setItem(CART_KEY, JSON.stringify(cart));
};

export const clearCart = () => {
  sessionStorage.removeItem(CART_KEY);
};

export const getCartTotal = () => {
  const cart = getCart();
  return cart.items.reduce((total, item) => total + item.price * item.quantity, 0);
};

export const setReservation = (reservationId: string, pin: string) => {
  const cart = getCart();
  cart.reservationId = reservationId;
  cart.pin = pin;
  sessionStorage.setItem(CART_KEY, JSON.stringify(cart));
};

export const getReservation = () => {
  const cart = getCart();
  return {
    reservationId: cart.reservationId,
    pin: cart.pin,
  };
};
