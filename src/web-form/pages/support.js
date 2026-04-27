import Head from 'next/head';
import { useRouter } from 'next/router';
import SupportForm from '../src/SupportForm';

export default function SupportPage() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Submit Support Request - Customer Success FTE</title>
        <meta name="description" content="Submit your support request and get instant AI-powered assistance" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <button
          onClick={() => router.push('/')}
          className="mb-4 flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to Home</span>
        </button>
        <SupportForm apiEndpoint="https://fte-backend-3ohm.onrender.com/support/submit" />
      </div>
    </>
  );
}
