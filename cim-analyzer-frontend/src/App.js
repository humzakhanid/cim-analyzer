import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/clerk-react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./Dashboard";
import AnalysisPage from "./AnalysisPage";

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      <SignedOut>
        <div className="text-center max-w-md mx-auto px-6">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Welcome to
            </h1>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              CIMLens
            </h1>
            <p className="text-gray-600 mt-4 text-lg">
              AI-powered investment analysis for CIMs
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <SignInButton mode="modal">
              <button className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-semibold text-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200 font-semibold text-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
                Sign Up
              </button>
            </SignUpButton>
          </div>
          
          <div className="mt-8 text-sm text-gray-500">
            <p>Upload CIMs • Get AI Analysis • Track Investments</p>
          </div>
        </div>
      </SignedOut>
      <SignedIn>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analysis/:id" element={<AnalysisPage />} />
        </Routes>
      </SignedIn>
    </div>
  );
}

export default App;
