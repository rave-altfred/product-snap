import { ArrowRight } from 'lucide-react'
import banner1 from '../assets/banner1.png'
import banner2 from '../assets/banner2.png'
import banner3 from '../assets/banner3.png'

export default function ProcessBanner() {
  return (
    <section className="bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-primary-950 dark:to-accent-950 pt-12 pb-16">
      <div className="container mx-auto px-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900 dark:text-white">
            Transform Any Photo in <span className="text-gradient">3 Simple Steps</span>
          </h2>
          <p className="text-lg text-gray-800 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            See how effortlessly you can turn a quick phone snapshot into stunning, 
            professional product photography that drives sales.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
          {/* Step 1 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-xl shadow-xl group-hover:shadow-2xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner1} 
                alt="Original phone photo" 
                className="w-full h-56 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-3 left-0 right-0 bg-black/80 backdrop-blur-sm h-16">
                <div className="px-4 py-3 text-white h-full flex flex-col justify-center">
                  <h3 className="text-base font-bold mb-0.5">Take Any Photo</h3>
                  <p className="text-xs text-gray-200">Quick snap with your phone - no setup required</p>
                </div>
              </div>
            </div>
            
            {/* Arrow for desktop */}
            <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 translate-x-1/2 z-10">
              <div className="bg-black/80 backdrop-blur-sm rounded-full p-4 shadow-xl border-2 border-white/20">
                <ArrowRight className="text-white" size={24} />
              </div>
            </div>
            
            {/* Arrow for mobile */}
            <div className="lg:hidden flex justify-center mt-4 mb-4">
              <div className="bg-white dark:bg-gray-800 rounded-full p-2 shadow-lg border-2 border-primary-200 dark:border-primary-700 rotate-90">
                <ArrowRight className="text-primary-600 dark:text-primary-400" size={16} />
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-xl shadow-xl group-hover:shadow-2xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner2} 
                alt="AI processing magic" 
                className="w-full h-56 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-3 left-0 right-0 bg-black/80 backdrop-blur-sm h-16">
                <div className="px-4 py-3 text-white h-full flex flex-col justify-center">
                  <h3 className="text-base font-bold mb-0.5">AI Magic Happens</h3>
                  <p className="text-xs text-gray-200">Our AI instantly processes and enhances</p>
                </div>
              </div>
            </div>
            
            {/* Arrow for desktop */}
            <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 translate-x-1/2 z-10">
              <div className="bg-black/80 backdrop-blur-sm rounded-full p-4 shadow-xl border-2 border-white/20">
                <ArrowRight className="text-white" size={24} />
              </div>
            </div>
            
            {/* Arrow for mobile */}
            <div className="lg:hidden flex justify-center mt-4 mb-4">
              <div className="bg-white dark:bg-gray-800 rounded-full p-2 shadow-lg border-2 border-accent-200 dark:border-accent-700 rotate-90">
                <ArrowRight className="text-accent-600 dark:text-accent-400" size={16} />
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="group relative">
            <div className="relative overflow-hidden rounded-xl shadow-xl group-hover:shadow-2xl transition-all duration-500 group-hover:scale-105">
              <img 
                src={banner3} 
                alt="Professional result" 
                className="w-full h-56 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              <div className="absolute bottom-3 left-0 right-0 bg-black/80 backdrop-blur-sm h-16">
                <div className="px-4 py-3 text-white h-full flex flex-col justify-center">
                  <h3 className="text-base font-bold mb-0.5">Professional Result</h3>
                  <p className="text-xs text-gray-200">Studio-quality photo ready for your store</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to action */}
        <div className="text-center mt-16">
          <div className="inline-flex flex-col sm:flex-row gap-4 items-center">
            <div className="text-lg text-gray-800 dark:text-gray-300 font-medium">
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
          <p className="text-sm text-gray-700 dark:text-gray-400 mt-4">
            ✨ No setup • No credit card • 5 free transformations
          </p>
        </div>
      </div>
    </section>
  )
}