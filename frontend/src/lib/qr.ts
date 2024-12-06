import QRCode from 'qrcode';

export const generateQRCode = async (itemId: string): Promise<string> => {
  const url = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/orders/${itemId}`;
  return QRCode.toDataURL(url);
};

export const generateQRLabel = async (item: { id: string; name: string; price: number }): Promise<string> => {
  const qrCode = await generateQRCode(item.id);
  const labelHtml = `
    <div style="padding: 20px; text-align: center;">
      <h2>${item.name}</h2>
      <p>Price: $${item.price.toFixed(2)}</p>
      <img src="${qrCode}" alt="QR Code" style="width: 200px; height: 200px;"/>
    </div>
  `;
  return labelHtml;
};
