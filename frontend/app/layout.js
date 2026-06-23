import './globals.css';

export const metadata = {
  title: 'DocuRAG — Ask your documents',
  description: 'Turn any document into a chatbot that answers with sources.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
