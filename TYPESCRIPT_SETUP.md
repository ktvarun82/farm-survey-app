# TypeScript Setup Guide

The frontend of the Farm Survey application has been migrated from JavaScript to TypeScript for better type safety, IDE support, and maintainability.

## 📁 Project Structure

```
src/
├── app.ts          # Main application logic (TypeScript)
└── types.ts        # Type definitions for API responses

static/js/
└── app.js          # Compiled JavaScript (generated, do not edit)
```

## 🛠️ Build Process

The TypeScript code is compiled to JavaScript using **esbuild** for fast bundling.

### Build Commands

```bash
# Compile TypeScript to JavaScript (one-time)
npm run build

# Watch mode - automatically recompile on file changes
npm run watch
# or
npm run dev
```

### Build Output

- **Input**: `src/app.ts` + `src/types.ts`
- **Output**: `static/js/app.js` (bundled, minified-ready)
- **Format**: IIFE (Immediately Invoked Function Expression) for browser compatibility
- **Target**: ES2020

## 🔧 Development Workflow

1. **Edit TypeScript files** in the `src/` directory
2. **Compile** using `npm run build` or use watch mode
3. **Refresh browser** to see changes

### Recommended Workflow

```bash
# Terminal 1: Watch for TypeScript changes
npm run watch

# Terminal 2: Run FastAPI server
uvicorn main:app --reload
```

## 📝 Type Definitions

Type definitions are located in `src/types.ts`:

- `GeoLocation` - Geographic coordinates
- `FarmSurvey` - Complete survey object
- `FarmSurveyCreate` - Survey creation payload
- `FarmSurveyUpdate` - Survey update payload
- `ApiError` - API error response

## ✨ Benefits of TypeScript

1. **Type Safety**: Catch errors at compile-time
2. **Better IDE Support**: Autocomplete, refactoring, navigation
3. **Self-Documenting**: Types serve as inline documentation
4. **Easier Refactoring**: Safe renaming and restructuring
5. **Future-Proof**: Modern standard for JavaScript development

## 🔍 Type Checking

The TypeScript compiler enforces:

- Strict null checks
- No implicit any types
- Strict function types
- Unused variable detection
- Unused parameter detection
- Implicit return checks

## 📦 Dependencies

- **typescript**: TypeScript compiler and type checker
- **esbuild**: Fast JavaScript bundler and minifier

See `package.json` for version details.

## 🚀 Production Build

For production, you may want to minify the output:

```bash
# Add --minify flag to esbuild command in package.json
esbuild src/app.ts --bundle --format=iife --outfile=static/js/app.js --target=es2020 --minify
```

## 📚 Resources

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [esbuild Documentation](https://esbuild.github.io/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

---

**Note**: Always compile TypeScript before deploying. The `static/js/app.js` file is generated and should not be edited directly.


