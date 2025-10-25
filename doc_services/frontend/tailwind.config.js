/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Parsey
        parsey: {
          blue: '#3B82F6',
          violet: '#6366F1',
          indigo: '#1E3A8A',
          lilac: '#A5B4FC',
          cyan: '#22D3EE',
          gray: '#64748B',
          bg: '#F3F4F6',
          white: '#F9FAFB',
          ink: '#0F172A',
        },
        // Cores semânticas
        brand: {
          primary: '#6366F1',      // violetInsight
          emphasis: '#1E3A8A',     // deepIndigo
          secondary: '#3B82F6',    // parseyBlue
          accent: '#22D3EE',       // dataCyan
          highlight: '#A5B4FC',    // softLilac
        },
        semantic: {
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          info: '#22D3EE',
        },
        border: {
          subtle: '#E5E7EB',
          default: '#CBD5E1',
          strong: '#64748B',
          focus: '#3B82F6',
        },
        text: {
          primary: '#0F172A',
          secondary: '#334155',
          muted: '#64748B',
        },
        bg: {
          default: '#F3F4F6',
          surface: '#F9FAFB',
          elevated: '#FFFFFF',
        },
        chart: {
          cat1: '#3B82F6',
          cat2: '#6366F1',
          cat3: '#22D3EE',
          cat4: '#A5B4FC',
          cat5: '#1E3A8A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'Inter', 'sans-serif'],
        mascot: ['Nunito', 'Inter', 'sans-serif'],
      },
      fontSize: {
        'xs': '12px',
        'sm': '14px',
        'md': '16px',
        'lg': '18px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '30px',
        '4xl': '36px',
        '5xl': '48px',
      },
      borderRadius: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
        'pill': '9999px',
        'parsey': '24px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(15, 23, 42, 0.06)',
        'md': '0 4px 12px rgba(15, 23, 42, 0.08)',
        'lg': '0 10px 24px rgba(15, 23, 42, 0.10)',
        'parsey': '0 8px 30px rgba(99, 102, 241, 0.2)',
        'accent': '0 0 0 6px rgba(34, 211, 238, 0.2)',
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'bounce-soft': 'bounceSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      transitionDuration: {
        'instant': '75ms',
        'fast': '150ms',
        'base': '250ms',
        'slow': '400ms',
      },
      transitionTimingFunction: {
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
      },
    },
  },
  plugins: [],
}
