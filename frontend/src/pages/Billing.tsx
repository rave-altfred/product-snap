import { useState, useEffect, useCallback } from 'react'
import { Check, CreditCard, Calendar, AlertCircle } from 'lucide-react'
import { api } from '../lib/api'

interface Plan {
  id: string
  name: string
  price: number
  currency: string
  interval: string
  yearly_price?: number
  yearly_savings?: string
  features: string[]
}

interface Subscription {
  plan: string
  status: string
  current_period_end: string | null
  paypal_subscription_id: string | null
}

interface PaymentHistoryItem {
  id: string
  amount: number
  currency: string
  status: string
  description: string | null
  created_at: string
}

export default function Billing() {
  // v2.1 - Testing cache
  const [plans, setPlans] = useState<Plan[]>([])
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [payments, setPayments] = useState<PaymentHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [billingInterval, setBillingInterval] = useState<'monthly' | 'yearly'>('monthly')

  const handleCancelPending = useCallback(async () => {
    try {
      setError(null)
      await api.post('/api/subscriptions/cancel-pending')
      await fetchData()
    } catch (err: any) {
      setError(err.message || 'Failed to cancel pending subscription')
    }
  }, [])

  useEffect(() => {
    fetchData()
    
    // Auto-cancel if returning from PayPal with cancel=true
    const params = new URLSearchParams(window.location.search)
    if (params.get('cancel') === 'true') {
      handleCancelPending()
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [handleCancelPending])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [plansResponse, subResponse, paymentsResponse] = await Promise.all([
        api.get('/api/subscriptions/plans'),
        api.get('/api/subscriptions/me'),
        api.get('/api/subscriptions/payments')
      ])
      setPlans(plansResponse.data.plans || [])
      setSubscription(subResponse.data)
      setPayments(paymentsResponse.data || [])
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


  const getPaidPlans = () => {
    // Filter out free plan since we show it manually
    return plans.filter(plan => plan.id !== 'free')
  }

  const getFreePlan = (): Plan => ({
    id: 'free',
    name: 'Free',
    price: 0,
    currency: 'USD',
    interval: 'month',
    features: [
      '5 image generations',
      'All three modes',
      'Watermarked outputs'
    ]
  })

  const getCurrentPlanName = () => {
    if (!subscription) return 'Free'
    const plan = subscription.plan.replace('_monthly', '').replace('_yearly', '')
    return plan.charAt(0).toUpperCase() + plan.slice(1)
  }

  return (
    <div className="p-8 max-w-6xl mx-auto animate-fade-in" style={{ opacity: loading ? 0.5 : 1, transition: 'opacity 0.15s ease-in-out' }}>
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
        
        {/* Pending subscription alert */}
        {subscription?.status === 'pending' && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
              <div className="flex-grow">
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-200">Payment Pending</h3>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mb-3">
                  Your subscription payment is pending. Complete the payment with PayPal or cancel to choose a different plan.
                </p>
                <button
                  onClick={handleCancelPending}
                  className="text-sm text-yellow-900 dark:text-yellow-200 underline hover:no-underline font-medium"
                >
                  Cancel pending subscription
                </button>
              </div>
            </div>
          </div>
        )}
        
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
          {subscription && subscription.plan !== 'free' && subscription.status === 'active' && (
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

        <div className="grid md:grid-cols-3 gap-6">
          {/* Free Plan */}
          {(() => {
            const freePlan = getFreePlan()
            return (
              <div
                key={freePlan.id}
                className={`card-flat border-2 transition-all flex flex-col ${
                  subscription?.plan === 'free' || !subscription
                    ? 'border-primary-500 dark:border-primary-600'
                    : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-2">STARTER</div>
                <h3 className="text-2xl font-bold mb-4">{freePlan.name}</h3>
                <div className="mb-6">
                  <span className="text-5xl font-extrabold">${freePlan.price}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-2">/month</span>
                </div>
                <ul className="space-y-3 mb-8 text-gray-600 dark:text-gray-300 flex-grow">
                  {freePlan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  disabled={subscription?.plan === 'free' || !subscription}
                  className={`btn w-full ${
                    subscription?.plan === 'free' || !subscription
                      ? 'btn-secondary cursor-not-allowed'
                      : 'btn-primary'
                  }`}
                >
                  {subscription?.plan === 'free' || !subscription ? 'Current Plan' : 'Downgrade'}
                </button>
              </div>
            )
          })()}
          
          {/* Basic and Pro Plans */}
          {getPaidPlans().map((plan) => {
            const isBasicPlan = plan.name.toLowerCase() === 'basic'
            const displayPrice = billingInterval === 'monthly' ? plan.price : plan.yearly_price
            const displayInterval = billingInterval === 'monthly' ? 'month' : 'year'
            
            return (
              <div
                key={plan.id}
                className={`card flex flex-col ${isBasicPlan ? 'border-2 border-primary-500 dark:border-primary-600 relative overflow-hidden' : 'border-2 border-transparent hover:border-gray-300 dark:hover:border-gray-600'} transition-all`}
              >
                {isBasicPlan && (
                  <div className="absolute top-0 right-0 bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
                    POPULAR
                  </div>
                )}
                <div className="text-sm font-semibold text-primary-600 dark:text-primary-400 mb-2">
                  {plan.name.toUpperCase()}
                </div>
                <h3 className="text-2xl font-bold mb-4">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-5xl font-extrabold">${displayPrice}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-2">/{displayInterval}</span>
                </div>
                {billingInterval === 'yearly' && plan.yearly_savings && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                    <span className="text-success-600 font-semibold">{plan.yearly_savings}</span>
                  </div>
                )}
                <ul className="space-y-3 mb-8 text-gray-600 dark:text-gray-300 flex-grow">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check className="text-success-600 flex-shrink-0 mt-0.5" size={20} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleSubscribe(`${plan.id}_${billingInterval === 'monthly' ? 'monthly' : 'yearly'}`)}
                  disabled={subscription?.plan === `${plan.id}_${billingInterval === 'monthly' ? 'monthly' : 'yearly'}` && subscription?.status === 'active' || subscription?.status === 'pending'}
                  className={`btn w-full ${
                    subscription?.plan === `${plan.id}_${billingInterval === 'monthly' ? 'monthly' : 'yearly'}` && subscription?.status === 'active'
                      ? 'btn-secondary cursor-not-allowed'
                      : subscription?.status === 'pending'
                      ? 'btn-secondary cursor-not-allowed opacity-50'
                      : 'btn-primary'
                  }`}
                >
                  {subscription?.plan === `${plan.id}_${billingInterval === 'monthly' ? 'monthly' : 'yearly'}` && subscription?.status === 'active' 
                    ? 'Current Plan' 
                    : subscription?.status === 'pending'
                    ? 'Payment Pending...'
                    : 'Subscribe'}
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Billing History */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Billing History</h2>
        {payments.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <CreditCard size={48} className="mx-auto mb-4 opacity-50" />
            <p>No billing history yet</p>
            <p className="text-sm mt-2">Your invoices will appear here</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-gray-200 dark:border-gray-700">
                <tr className="text-left text-sm text-gray-500 dark:text-gray-400">
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium">Description</th>
                  <th className="pb-3 font-medium text-right">Amount</th>
                  <th className="pb-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {payments.map((payment) => (
                  <tr key={payment.id} className="text-sm">
                    <td className="py-4 text-gray-900 dark:text-gray-100">
                      {new Date(payment.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </td>
                    <td className="py-4 text-gray-600 dark:text-gray-300">
                      {payment.description || 'Subscription payment'}
                    </td>
                    <td className="py-4 text-right text-gray-900 dark:text-gray-100 font-medium">
                      ${payment.amount.toFixed(2)} {payment.currency}
                    </td>
                    <td className="py-4 text-right">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        payment.status === 'completed'
                          ? 'bg-success-100 dark:bg-success-900/20 text-success-700 dark:text-success-400'
                          : payment.status === 'refunded'
                          ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400'
                          : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                      }`}>
                        {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
