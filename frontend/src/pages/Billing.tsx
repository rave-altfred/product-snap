import { useState, useEffect } from 'react'
import { Check, CreditCard, Calendar, AlertCircle } from 'lucide-react'
import { api } from '../lib/api'

interface Plan {
  id: string
  name: string
  price: number
  currency: string
  interval: string
  savings?: string
  features: string[]
}

interface Subscription {
  plan: string
  status: string
  current_period_end: string | null
  paypal_subscription_id: string | null
}

export default function Billing() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPlan] = useState<string | null>(null)
  const [billingInterval, setBillingInterval] = useState<'monthly' | 'yearly'>('monthly')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [plansResponse, subResponse] = await Promise.all([
        api.get('/api/subscriptions/plans'),
        api.get('/api/subscriptions/me')
      ])
      setPlans(plansResponse.data.plans || [])
      setSubscription(subResponse.data)
    } catch (err: any) {
      setError(err.message || 'Failed to load billing information')
    } finally {
      setLoading(false)
    }
  }

  const handleSubscribe = async (planId: string) => {
    try {
      setError(null)
      const response = await api.post('/api/subscriptions/create', {
        plan: planId,
        return_url: `${window.location.origin}/billing?success=true`,
        cancel_url: `${window.location.origin}/billing?cancel=true`
      })
      
      // Redirect to PayPal approval URL
      if (response.data.approval_url) {
        window.location.href = response.data.approval_url
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create subscription')
    }
  }

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return
    
    try {
      setError(null)
      await api.post('/api/subscriptions/cancel')
      await fetchData()
      alert('Subscription cancelled successfully')
    } catch (err: any) {
      setError(err.message || 'Failed to cancel subscription')
    }
  }

  const getFilteredPlans = () => {
    return plans.filter(plan => {
      if (plan.id === 'free') return false
      if (billingInterval === 'monthly') {
        return plan.interval === 'month'
      } else {
        return plan.interval === 'year'
      }
    })
  }

  const getCurrentPlanName = () => {
    if (!subscription) return 'Free'
    const plan = subscription.plan.replace('_monthly', '').replace('_yearly', '')
    return plan.charAt(0).toUpperCase() + plan.slice(1)
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-8"></div>
          <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Billing & Subscriptions</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">Manage your subscription and payment methods</p>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-900 dark:text-red-200">Error</h3>
            <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Current Subscription */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold mb-4">Current Plan</h2>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
              <CreditCard className="text-primary-600 dark:text-primary-400" size={24} />
            </div>
            <div>
              <h3 className="font-bold text-lg">{getCurrentPlanName()} Plan</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Status: <span className="capitalize font-medium">{subscription?.status || 'active'}</span>
              </p>
              {subscription?.current_period_end && (
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <Calendar size={14} />
                  Renews on {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
          {subscription && subscription.plan !== 'free' && (
            <button
              onClick={handleCancelSubscription}
              className="btn btn-secondary text-sm"
            >
              Cancel Subscription
            </button>
          )}
        </div>
      </div>

      {/* Plan Selection */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Choose Your Plan</h2>
          <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 p-1 bg-gray-50 dark:bg-gray-800">
            <button
              onClick={() => setBillingInterval('monthly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingInterval === 'monthly'
                  ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingInterval('yearly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingInterval === 'yearly'
                  ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Yearly <span className="text-success-600 ml-1">(Save 17%)</span>
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {getFilteredPlans().map((plan) => (
            <div
              key={plan.id}
              className={`card border-2 transition-all ${
                selectedPlan === plan.id
                  ? 'border-primary-500 dark:border-primary-600'
                  : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                  <div className="mt-2">
                    <span className="text-3xl font-extrabold">${plan.price}</span>
                    <span className="text-gray-500 dark:text-gray-400 ml-1">/{plan.interval}</span>
                  </div>
                  {plan.savings && (
                    <div className="text-sm text-success-600 font-semibold mt-1">
                      Save {plan.savings}
                    </div>
                  )}
                </div>
              </div>

              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <Check className="text-success-600 flex-shrink-0 mt-0.5" size={16} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={subscription?.plan === plan.id}
                className={`btn w-full ${
                  subscription?.plan === plan.id
                    ? 'btn-secondary cursor-not-allowed'
                    : 'btn-primary'
                }`}
              >
                {subscription?.plan === plan.id ? 'Current Plan' : 'Subscribe'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Billing History */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Billing History</h2>
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <CreditCard size={48} className="mx-auto mb-4 opacity-50" />
          <p>No billing history yet</p>
          <p className="text-sm mt-2">Your invoices will appear here</p>
        </div>
      </div>
    </div>
  )
}
