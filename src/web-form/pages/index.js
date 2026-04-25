import Head from 'next/head';
import App from '../src/App';

export default function Home() {
  return (
    <>
      <Head>
        <title>Customer Success FTE - AI-Powered Multi-Channel Support</title>
        <meta name="description" content="24/7 AI-powered support across Email, WhatsApp, and Web. Real-time chat, voice support, analytics, and more." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <App />
    </>
  );
}
