import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { CreditCard, RotateCcw, ChevronLeft, ChevronRight, Plus } from 'lucide-react';

function FlashcardsPage() {
  const [topics, setTopics] = useState([]);
  const [flashcardSets, setFlashcardSets] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [numCards, setNumCards] = useState(10);
  const [currentSet, setCurrentSet] = useState(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTopics();
    fetchFlashcardSets();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await axios.get('/api/documents/topics');
      setTopics(response.data.topics);
    } catch (error) {
      console.error('Error fetching topics:', error);
      toast.error('Failed to load topics');
    }
  };

  const fetchFlashcardSets = async () => {
    try {
      const response = await axios.get('/api/flashcards/');
      setFlashcardSets(response.data.flashcard_sets);
    } catch (error) {
      console.error('Error fetching flashcard sets:', error);
      toast.error('Failed to load flashcard sets');
    }
  };

  const generateFlashcards = async () => {
    if (!selectedTopic) {
      toast.error('Please select a topic');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/flashcards/generate', {
        topic: selectedTopic,
        num_cards: numCards
      });

      const newSet = response.data.flashcard_set;
      setCurrentSet(newSet);
      setCurrentCard(0);
      setShowAnswer(false);
      setFlashcardSets(prev => [newSet, ...prev]);
      toast.success('Flashcards generated successfully!');
    } catch (error) {
      console.error('Error generating flashcards:', error);
      toast.error('Failed to generate flashcards');
    } finally {
      setLoading(false);
    }
  };

  const selectSet = (set) => {
    setCurrentSet(set);
    setCurrentCard(0);
    setShowAnswer(false);
  };

  const nextCard = () => {
    if (currentCard < currentSet.cards.length - 1) {
      setCurrentCard(currentCard + 1);
      setShowAnswer(false);
    }
  };

  const prevCard = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
      setShowAnswer(false);
    }
  };

  const flipCard = () => {
    setShowAnswer(!showAnswer);
  };

  const resetSet = () => {
    setCurrentCard(0);
    setShowAnswer(false);
  };

  if (currentSet) {
    const card = currentSet.cards[currentCard];
    const progress = ((currentCard + 1) / currentSet.cards.length) * 100;

    return (
      <div className="space-y-6">
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="card-title">Flashcards: {currentSet.topic}</h1>
                <p className="card-description">
                  Card {currentCard + 1} of {currentSet.cards.length}
                </p>
              </div>
              <div className="flex space-x-2">
                <button onClick={resetSet} className="btn-secondary">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </button>
                <button onClick={() => setCurrentSet(null)} className="btn-secondary">
                  Back to Sets
                </button>
              </div>
            </div>
            <div className="w-full bg-primary-200 rounded-full h-2 mt-4">
              <div
                className="bg-accent-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <div className="w-full max-w-2xl">
            <div
              className="card cursor-pointer transform transition-transform hover:scale-105"
              onClick={flipCard}
              style={{ minHeight: '300px' }}
            >
              <div className="card-content flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="mb-4">
                    <span className="text-sm text-primary-500 uppercase tracking-wide">
                      {showAnswer ? 'Answer' : 'Question'}
                    </span>
                  </div>
                  <div className="text-xl font-medium text-primary-900 leading-relaxed">
                    {showAnswer ? card.answer : card.question}
                  </div>
                  <div className="mt-6">
                    <p className="text-sm text-primary-500">
                      Click to {showAnswer ? 'show question' : 'reveal answer'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center space-x-4">
          <button
            onClick={prevCard}
            disabled={currentCard === 0}
            className="btn-secondary"
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </button>
          
          <button onClick={flipCard} className="btn-primary">
            {showAnswer ? 'Show Question' : 'Show Answer'}
          </button>
          
          <button
            onClick={nextCard}
            disabled={currentCard === currentSet.cards.length - 1}
            className="btn-secondary"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-2" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-3">
            <CreditCard className="h-8 w-8 text-accent-600" />
            <div>
              <h1 className="card-title">Flashcards</h1>
              <p className="card-description">
                Review key concepts with AI-generated flashcards
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Generate New Flashcards */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Generate New Flashcards</h2>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Select Topic
              </label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="input"
              >
                <option value="">Choose a topic...</option>
                {topics.map((topic) => (
                  <option key={topic} value={topic}>
                    {topic}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Number of Cards
              </label>
              <select
                value={numCards}
                onChange={(e) => setNumCards(parseInt(e.target.value))}
                className="input"
              >
                <option value={5}>5 Cards</option>
                <option value={10}>10 Cards</option>
                <option value={15}>15 Cards</option>
                <option value={20}>20 Cards</option>
              </select>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={generateFlashcards}
              disabled={loading || !selectedTopic}
              className="btn-primary"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </div>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Generate Flashcards
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Existing Flashcard Sets */}
      {flashcardSets.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Your Flashcard Sets</h2>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {flashcardSets.map((set) => (
                <div
                  key={set.id}
                  className="p-4 border border-primary-200 rounded-lg hover:border-accent-300 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => selectSet(set)}
                >
                  <h3 className="font-medium text-primary-900 mb-2">{set.topic}</h3>
                  <p className="text-sm text-primary-600 mb-3">
                    {set.cards.length} cards
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-primary-500">
                      {new Date(set.created_at).toLocaleDateString()}
                    </span>
                    <CreditCard className="h-4 w-4 text-accent-500" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {topics.length === 0 && (
        <div className="card">
          <div className="card-content text-center py-8">
            <CreditCard className="h-12 w-12 text-primary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary-900 mb-2">
              No Topics Available
            </h3>
            <p className="text-primary-600">
              Upload some study materials first to generate flashcards.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default FlashcardsPage;
