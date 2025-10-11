import { ArrowRight } from 'lucide-react'
import banner1 from '../assets/banner1.png'
import banner2 from '../assets/banner2.png'
import banner3 from '../assets/banner3.png'

export default function ProcessBanner() {
  return (
    <section className="bg-gradient-to-br from-primary-50 to-accent-50 dark:from-primary-950 dark:to-accent-950 py-24">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <div className="inline-block px-4 py-2 bg-white/80 dark:bg-gray-800/80 rounded-full mb-6 backdrop-blur-sm border border-primary-200 dark:border-primary-700">
            <span className="text-primary-700 dark:text-primary-300 font-semibold text-sm">📸 From Phone to Professional</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            Transform Any Photo in <span className="text-gradient">3 Simple Steps</span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            See how effortlessly you can turn a quick phone snapshot into stunning, 
            professional product photography that drives sales.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 lg:gap-12 max-w-7xl mx-auto">
          {/* Step 1 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-2xl shadow-2xl group-hover:shadow-3xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner1} 
                alt="Original phone photo" 
                className="w-full h-80 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-4 left-0 right-0 bg-black/80 backdrop-blur-sm h-20">
                <div className="px-6 py-4 text-white h-full flex flex-col justify-center">
                  <h3 className="text-lg font-bold mb-1">Take Any Photo</h3>
                  <p className="text-sm text-gray-200">Quick snap with your phone - no setup required</p>
                </div>
              </div>
            </div>
            
            {/* Arrow for desktop */}
            <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2 translate-x-1/2 z-10">
              <div className="bg-black/80 backdrop-blur-sm rounded-full p-6 shadow-2xl border-4 border-white/20">
                <ArrowRight className="text-white" size={32} />
              </div>
            </div>
            
            {/* Arrow for mobile */}
            <div className="lg:hidden flex justify-center mt-6 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-full p-3 shadow-lg border-2 border-primary-200 dark:border-primary-700 rotate-90">
                <ArrowRight className="text-primary-600 dark:text-primary-400" size={20} />
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-2xl shadow-2xl group-hover:shadow-3xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner2} 
                alt="AI processing magic" 
                className="w-full h-80 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-4 left-0 right-0 bg-black/80 backdrop-blur-sm h-20">
                <div className="px-6 py-4 text-white h-full flex flex-col justify-center">
                  <h3 className="text-lg font-bold mb-1">AI Magic Happens</h3>
                  <p className="text-sm text-gray-200">Our AI instantly processes and enhances</p>
                </div>
              </div>
            </div>
            
            {/* Arrow for desktop */}
            <div className="hidden lg:block absolute top-1/2 -right-6 transform -translate-y-1/2 translate-x-1/2 z-10">
              <div className="bg-black/80 backdrop-blur-sm rounded-full p-6 shadow-2xl border-4 border-white/20">
                <ArrowRight className="text-white" size={32} />
              </div>
            </div>
            
            {/* Arrow for mobile */}
            <div className="lg:hidden flex justify-center mt-6 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-full p-3 shadow-lg border-2 border-accent-200 dark:border-accent-700 rotate-90">
                <ArrowRight className="text-accent-600 dark:text-accent-400" size={20} />
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-2xl shadow-2xl group-hover:shadow-3xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner3} 
                alt="Professional result" 
                className="w-full h-80 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-4 left-0 right-0 bg-black/80 backdrop-blur-sm h-20">
                <div className="px-6 py-4 text-white h-full flex flex-col justify-center">
                  <h3 className="text-lg font-bold mb-1">Professional Result</h3>
                  <p className="text-sm text-gray-200">Studio-quality photo ready for your store</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to action */}
        <div className="text-center mt-16">
          <div className="inline-flex flex-col sm:flex-row gap-4 items-center">
            <div className="text-lg text-gray-600 dark:text-gray-300 font-medium">
              Ready to transform your photos?
            </div>
            <div className="flex gap-3">
              <a href="/register" className="btn btn-primary text-lg px-8 py-3 group">
                Try It Free
                <ArrowRight className="inline ml-2 group-hover:translate-x-1 transition-transform" size={18} />
              </a>
              <a href="#features" className="btn btn-secondary text-lg px-8 py-3">
                Learn More
              </a>
            </div>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
            ✨ No setup • No credit card • 5 free transformations
          </p>
        </div>
      </div>
    </section>
  )
}